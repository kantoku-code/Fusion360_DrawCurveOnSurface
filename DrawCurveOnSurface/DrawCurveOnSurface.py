#FusionAPI_python Addin
#Author-kantoku
#Description-

#using Fusion360AddinSkeleton
#https://github.com/tapnair/Fusion360AddinSkeleton
#Special thanks:Patrick Rainsberry

from .DrawCurveOnSurfaceCore import DrawCurveOnSurfaceCore

commands = []
command_definitions = []

# Set to True to display various useful messages when debugging your app
debug = False

def run(context):

    cmd = {
        'cmd_name': '面上の線',
        'cmd_description': '指定した面上に線を描きます',
        'cmd_id': 'drawcurve_onface',
        'cmd_resources': 'resources',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': 'SketchPanel',
        'class': DrawCurveOnSurfaceCore
    }

    command_definitions.append(cmd)

    # Don't change anything below here:
    for cmd_def in command_definitions:
        command = cmd_def['class'](cmd_def, debug)
        commands.append(command)

        for run_command in commands:
            run_command.on_run()

def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
