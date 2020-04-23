# FusionAPI_python 
# Author-kantoku

import adsk.core, adsk.fusion, traceback

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


# CommandInputs
_selSurfInfo = ['dlgSelSurf','サポート面','線を描く面を選択']
_surfIpt = adsk.core.SelectionCommandInput.cast(None)

_selPointInfo = ['dlgSelPoint','頂点','頂点を選択']
_pointIpt = adsk.core.SelectionCommandInput.cast(None)



class DrawCurveOnSurfaceCore(Fusion360CommandBase):
    _handlers = []
    _skt = adsk.fusion.Sketch.cast(None)
    _fact = None

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)
        pass

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        try:
            global _fact, _surfIpt, _pointIpt
            if self._fact:
                self._fact.preview(
                    _surfIpt.selection(0).entity,
                    _pointIpt.selection(0).entity,
                    _pointIpt.selection(1).entity,
                    self._skt)

        except:
            if ao.ui:
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        self._fact = None

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        # 面をクリアすると点もクリア
        global _surfIpt, _pointIpt

        if changed_input == _surfIpt:
            if _surfIpt.selectionCount < 1:
                _pointIpt.clearSelection()
            else:
                _pointIpt.hasFocus = True

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        try:
            global _fact, _surfIpt, _pointIpt
            if self._fact:
                self._fact.execute(
                    _surfIpt.selection(0).entity,
                    _pointIpt.selection(0).entity,
                    _pointIpt.selection(1).entity,
                    self._skt)

        except:
            if ao.ui:
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        # sketch
        skt = adsk.fusion.Sketch.cast(ao.app.activeEditObject)
        if not skt: return

        self._skt = skt

        # comp position check
        command.isPositionDependent = True

        # factry
        self._fact = DrawCurveOnSurfaceFactry()

        # -- event --
        onValid = self.ValidateInputHandler()
        command.validateInputs.add(onValid)
        self._handlers.append(onValid)

        onPreSelect = self.PreSelectHandler()
        command.preSelect.add(onPreSelect)
        self._handlers.append(onPreSelect)

        # -- Dialog --
        global _selSurfInfo, _surfIpt

        # surf
        _surfIpt = inputs.addSelectionInput(
            _selSurfInfo[0], _selSurfInfo[1], _selSurfInfo[2])
        _surfIpt.setSelectionLimits(0)
        _surfIpt.addSelectionFilter('Faces')

        # point
        global _selPointInfo, _pointIpt
        _pointIpt = inputs.addSelectionInput(
            _selPointInfo[0], _selPointInfo[1], _selPointInfo[2])
        _pointIpt.setSelectionLimits(0)
        _pointIpt.addSelectionFilter('Vertices')


    # -- Support class --
    class PreSelectHandler(adsk.core.SelectionEventHandler):
        def __init__(self):
            super().__init__()

        # 要素選択は面選択されていることが前提
        def notify(self, args):
            try:
                args = adsk.core.SelectionEventArgs.cast(args)

                # unSelection
                actIpt = adsk.core.SelectionCommandInput.cast(
                    args.firingEvent.activeInput)
                if not actIpt: return

                global _surfIpt, _pointIpt

                # -- surf --
                if actIpt == _surfIpt:
                    args.isSelectable = False

                    # surf count
                    if _surfIpt.selectionCount < 1:
                        args.isSelectable = True

                    return


                # -- point --
                if actIpt == _pointIpt:
                    args.isSelectable = False

                    # point count
                    if _pointIpt.selectionCount > 1:
                        return

                    # surf count
                    if _surfIpt.selectionCount < 1:
                        return

                    # onFace?
                    vtx :adsk.fusion.BRepVertex = args.selection.entity
                    face :adsk.fusion.BRepFace = _surfIpt.selection(0).entity
                    vtxs = [v for v in face.vertices]
                    if vtx in vtxs:
                        args.isSelectable = True

                    return

            except:
                ao = AppObjects()
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    class ValidateInputHandler(adsk.core.ValidateInputsEventHandler):
        def __init__(self):
            super().__init__()
        def notify(self, args):
            global _surfIpt, _pointIpt
            if _surfIpt.selectionCount > 0 and _pointIpt.selectionCount > 1:
                args.areInputsValid = True
            else:
                args.areInputsValid = False

class DrawCurveOnSurfaceFactry():

    _cgGroup = adsk.fusion.CustomGraphicsGroup.cast(None)

    def __init__(self):
        self.refreshCG()

    def removeCG(self):
        ao = AppObjects()
        cgs = [cmp.customGraphicsGroups for cmp in ao.design.allComponents]
        cgs = [cg for cg in cgs if cg.count > 0]
        
        if len(cgs) < 1: return

        for cg in cgs:
            gps = [c for c in cg]
            gps.reverse()
            for gp in gps:
                gp.deleteMe()

    def refreshCG(self):
        self.removeCG()
        ao = AppObjects()
        self._cgGroup = ao.root_comp.customGraphicsGroups.add()

    def preview(
        self,
        surf :adsk.fusion.BRepFace,
        vtx1 :adsk.fusion.BRepVertex,
        vtx2 :adsk.fusion.BRepVertex,
        skt :adsk.fusion.Sketch
        ):

        self.refreshCG()

        crvs = self.__getCrv3d(
            surf.evaluator,
            vtx1.geometry,
            vtx2.geometry)
        if len(crvs) < 1: return

        red = adsk.core.Color.create(255,0,0,255)
        solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(red)

        mat3d :adsk.core.Matrix3D = skt.transform
        mat3d.invert()

        for crv in crvs:
            if hasattr(crv,'asNurbsCurve'):
                crv = crv.asNurbsCurve

            crvCg = self._cgGroup.addCurve(crv)
            crvCg.color = solidRed

    def execute(
        self,
        surf :adsk.fusion.BRepFace,
        vtx1 :adsk.fusion.BRepVertex,
        vtx2 :adsk.fusion.BRepVertex,
        skt :adsk.fusion.Sketch
        ):

        evaSurf = surf.evaluator
        crvs = self.__getCrv3d(
            evaSurf,
            vtx1.geometry,
            vtx2.geometry)
        
        if len(crvs) < 1: return

        sktCrvs = skt.sketchCurves
        mat3d :adsk.core.Matrix3D = skt.transform
        mat3d.invert()

        for crv in crvs:
            if hasattr(crv,'asNurbsCurve'):
                crv = crv.asNurbsCurve

            if crv.objectType == 'adsk::core::NurbsCurve3D':
                # 精度悪い
                # sktElm = sktCrvs.sketchFittedSplines.addByNurbsCurve(crv)

                evaCrv = crv.evaluator
                _, sprm, eprm = evaCrv.getParameterExtents()
                _, pnts = evaCrv.getStrokes(sprm, eprm, 0.01)
                _, prms = evaSurf.getParametersAtPoints(pnts)
                _, pnts = evaSurf.getPointsAtParameters(prms)

                points = adsk.core.ObjectCollection.create()
                [pnt.transformBy(mat3d) for pnt in pnts]
                [points.add(pnt) for pnt in pnts]

                sktElm = sktCrvs.sketchFittedSplines.add(points)

            else:
                s = crv.startPoint
                e = crv.endPoint
                sktElm = sktCrvs.sketchLines.addByTwoPoints(s,e)

            sktElm.isFixed = True
            skt.include(sktElm)
            sktElm.deleteMe()

        return

    def __getCrv3d(
        self,
        eva :adsk.core.SurfaceEvaluator,
        pnt1 :adsk.core.Point3D,
        pnt2 :adsk.core.Point3D
        ) -> list:

        res1, prm1 = eva.getParameterAtPoint(pnt1)
        if not res1 or not eva.isParameterOnFace(prm1):
            return []

        res2, prm2 = eva.getParameterAtPoint(pnt2)
        if not res2 or not eva.isParameterOnFace(prm2):
            return []

        line = adsk.core.Line2D.create(prm1,prm2)
        lst = eva.getModelCurveFromParametricCurve(line)
        if len(lst) < 1:
            # ここに失敗時の別処理入れたい
            return []

        return [v for v in lst]