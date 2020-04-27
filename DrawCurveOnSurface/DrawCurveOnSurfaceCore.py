# FusionAPI_python 
# Author-kantoku

import adsk.core, adsk.fusion, traceback

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


# CommandInputs
_selSurfInfo = ['dlgSelSurf','サポート面','線を描く面を選択']
_surfIpt = adsk.core.SelectionCommandInput.cast(None)

_selPointInfo = ['dlgSelPoint','始点終点','始点と終点を選択']
_pointIpt = adsk.core.SelectionCommandInput.cast(None)

_radFilterInfo = [
    'dlgFilter',
    'フィルター',
    ['頂点のみ', False],
    ['境界線上', True]]
_filterIpt = adsk.core.RadioButtonGroupCommandInput.cast(None)

_radToleranceInfo = [
    'dlgTolerance',
    'トレランス',
    ['High', False, 0.0001],
    ['Mid', False, 0.001],
    ['Low', True,0.01]]
_tolIpt = adsk.core.RadioButtonGroupCommandInput.cast(None)

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

            pnt1 = self.getPointByEntityType(_pointIpt.selection(0))
            pnt2 = self.getPointByEntityType(_pointIpt.selection(1))

            if self._fact:
                self._fact.preview(
                    _surfIpt.selection(0).entity,
                    pnt1,
                    pnt2)

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
        
        # フィルターの変更
        # エッジが選択済みで'頂点のみ'に切り替えた際、選択要素解除すべき？
        global _filterIpt
        if changed_input == _filterIpt:
            filter = _filterIpt.selectedItem.index
            _pointIpt.clearSelectionFilter()
            if filter == 0:
                _pointIpt.addSelectionFilter('Vertices')
            elif  filter == 1:
                _pointIpt.addSelectionFilter('Vertices')
                _pointIpt.addSelectionFilter('Edges')

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        try:
            global _fact, _surfIpt, _pointIpt

            pnt1 = self.getPointByEntityType(_pointIpt.selection(0))
            pnt2 = self.getPointByEntityType(_pointIpt.selection(1))

            global _radToleranceInfo, _tolIpt
            tol = _radToleranceInfo[_tolIpt.selectedItem.index +2][2]

            if self._fact:
                self._fact.execute(
                    _surfIpt.selection(0).entity,
                    pnt1,
                    pnt2,
                    self._skt,
                    tol
                    )

        except:
            if ao.ui:
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        # 事前選択禁止
        ao.ui.activeSelections.clear()

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
        _pointIpt.addSelectionFilter('Edges')

        # point filter
        global _radFilterInfo, _filterIpt
        _filterIpt = inputs.addRadioButtonGroupCommandInput(
            _radFilterInfo[0], _radFilterInfo[1])
        filters = _filterIpt.listItems
        filters.add(_radFilterInfo[2][0], _radFilterInfo[2][1])
        filters.add(_radFilterInfo[3][0], _radFilterInfo[3][1])

        # curve tolerance
        global _radToleranceInfo, _tolIpt 
        _tolIpt = inputs.addRadioButtonGroupCommandInput(
            _radToleranceInfo[0], _radToleranceInfo[1])
        tols = _tolIpt.listItems
        tols.add(_radToleranceInfo[2][0], _radToleranceInfo[2][1])
        tols.add(_radToleranceInfo[3][0], _radToleranceInfo[3][1])
        tols.add(_radToleranceInfo[4][0], _radToleranceInfo[4][1])

    # -- Support fanction --
    def getPointByEntityType(
        self,
        sel :adsk.core.Selection) -> adsk.core.Point3D:

        ent = sel.entity
        t = ent.objectType.split('::')[-1]
        if t == 'BRepVertex':
            return ent.geometry

        elif t == 'BRepEdge':
            eva :adsk.core.CurveEvaluator3D = ent.geometry.evaluator
            _, prm = eva.getParameterAtPoint(sel.point)
            _, pnt = eva.getPointAtParameter(prm)
            return pnt

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

                    # filter type
                    face :adsk.fusion.BRepFace = _surfIpt.selection(0).entity

                    global _filterIpt
                    filter = _filterIpt.selectedItem.index
                    if filter == 0:
                        if self.isOnVertex(args.selection.entity, face):
                            args.isSelectable = True

                    elif  filter == 1:
                        if self.isOnVertex(args.selection.entity, face):
                            args.isSelectable = True
                        if self.isOnEdge(args.selection.entity, face):
                            args.isSelectable = True

                    return

            except:
                ao = AppObjects()
                ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        def isOnEdge(
            self,
            ent,
            face :adsk.fusion.BRepFace) -> bool:

            edges = [e for e in face.edges]
            if ent in edges:
                return True
            else:
                return False

        def isOnVertex(
            self,
            ent,
            face :adsk.fusion.BRepFace) -> bool:

            vtxs = [v for v in face.vertices]
            if ent in vtxs:
                return True
            else:
                return False

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

    def __del__(self):
        self.removeCG()

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
        pnt1 :adsk.core.Point3D,
        pnt2 :adsk.core.Point3D,
        ):

        self.refreshCG()

        tmpBrep = adsk.fusion.TemporaryBRepManager.get()
        tmpSurf = tmpBrep.copy(surf)
        crvs = self.__getCrv3d(tmpSurf.faces[0].evaluator, pnt1, pnt2)
        if len(crvs) < 1: return

        red = adsk.core.Color.create(255,0,0,255)
        solidRed = adsk.fusion.CustomGraphicsSolidColorEffect.create(red)

        for crv in crvs:
            if hasattr(crv,'asNurbsCurve'):
                crv = crv.asNurbsCurve

            # crv.transformBy(mat)
            crvCg = self._cgGroup.addCurve(crv)
            crvCg.color = solidRed

    def execute(
        self,
        surf :adsk.fusion.BRepFace,
        pnt1 :adsk.core.Point3D,
        pnt2 :adsk.core.Point3D,
        skt :adsk.fusion.Sketch,
        tolerance :float = 0.01
        ):

        tmpBrep = adsk.fusion.TemporaryBRepManager.get()
        tmpSurf = tmpBrep.copy(surf)
        crvs = self.__getCrv3d(tmpSurf.faces[0].evaluator, pnt1, pnt2)

        evaSurf = surf.evaluator
        # crvs = self.__getCrv3d(surf.evaluator, pnt1, pnt2)
        if len(crvs) < 1: return

        sktCrvs = skt.sketchCurves
        mat3d :adsk.core.Matrix3D = skt.transform
        mat3d.invert()

        skt.isComputeDeferred = True
        for crv in crvs:
            if hasattr(crv,'asNurbsCurve'):
                crv = crv.asNurbsCurve

            if crv.objectType == 'adsk::core::NurbsCurve3D':
                evaCrv = crv.evaluator
                _, sprm, eprm = evaCrv.getParameterExtents()
                _, pnts = evaCrv.getStrokes(sprm, eprm, tolerance)
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

        skt.isComputeDeferred = False
        return

    def __getCrv3d(
        self,
        eva :adsk.core.SurfaceEvaluator,
        pnt1 :adsk.core.Point3D,
        pnt2 :adsk.core.Point3D
        ) -> list:

        res1, prm1 = eva.getParameterAtPoint(pnt1)
        hhh = eva.parametricRange()
        maxPrm = hhh.maxPoint
        minPrm = hhh.minPoint
        _,maxP = eva.getPointAtParameter(maxPrm)
        _,minP = eva.getPointAtParameter(minPrm)

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