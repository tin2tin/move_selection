bl_info = {
    "name": "Move Selection",
    "author": "tintwotin",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "Sequencer > Select > Move Selection",
    "description": "Moved the selection",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}

import bpy


class SEQUENCER_OT_move_selection(bpy.types.Operator):
    bl_idname = "sequencer.change_selection"
    bl_label = "Change Selection"

    # Define an enum property for direction
    direction_options = [
        ("LEFT", "Left", "Select the nearest strip to the left"),
        ("RIGHT", "Right", "Select the nearest strip to the right"),
        ("UP", "Above", "Select the nearest strip in the channel above"),
        ("DOWN", "Below", "Select the nearest strip in the channel below"),
    ]

    direction: bpy.props.EnumProperty(items=direction_options, default="LEFT")

    def execute(self, context):
        # Get the current active strip
        active_strip = context.scene.sequence_editor.active_strip

        if active_strip:
            # Get all the sequences in the VSE
            sequences = context.scene.sequence_editor.sequences_all

            # Deselect all strips
            for seq in sequences:
                seq.select = False
            # Initialize variables to track the nearest strip and its distance
            nearest_strip = None
            nearest_distance = float("inf")
            distance = None

            if self.direction == "LEFT" or self.direction == "RIGHT":
                for seq in sequences:
                    # Check if the sequence is not the active strip and is in the same channel
                    if seq != active_strip and seq.channel == active_strip.channel:
                        # Calculate the distance between the active strip and the current strip based on frames
                        if (
                            self.direction == "LEFT"
                            and active_strip.frame_final_start > seq.frame_final_end
                        ):
                            distance = (
                                active_strip.frame_final_start - seq.frame_final_end
                            )
                        elif (
                            self.direction == "RIGHT"
                            and seq.frame_final_start > active_strip.frame_final_end
                        ):
                            distance = (
                                seq.frame_final_start - active_strip.frame_final_end
                            )
                        # Update the nearest strip if this strip is closer
                        if distance and abs(distance) < nearest_distance:
                            nearest_distance = abs(distance)
                            nearest_strip = seq
            if self.direction == "UP":
                # If the direction is UP, find the nearest strip in the highest channel
                active_channel = active_strip.channel + 1
                highest_channel = max(
                    seq.channel for seq in sequences
                )  # Find the highest channel number
                while not nearest_strip and (active_channel <= highest_channel):
                    for seq in sequences:
                        if (
                            seq.channel
                            == active_channel  # Check if the sequence is in the channel above
                            and abs(
                                seq.frame_final_start
                                + (seq.frame_final_end - seq.frame_final_start) / 2
                                - (
                                    active_strip.frame_final_start
                                    + (
                                        active_strip.frame_final_end
                                        - active_strip.frame_final_start
                                    )
                                    / 2
                                )
                            )
                            < nearest_distance
                        ):
                            nearest_distance = abs(
                                seq.frame_final_start
                                + (seq.frame_final_end - seq.frame_final_start) / 2
                                - (
                                    active_strip.frame_final_start
                                    + (
                                        active_strip.frame_final_end
                                        - active_strip.frame_final_start
                                    )
                                    / 2
                                )
                            )
                            nearest_strip = seq
                    active_channel += 1
            if self.direction == "DOWN":
                # If the direction is DOWN, find the nearest strip in the lowest channel
                active_channel = active_strip.channel - 1
                lowest_channel = min(
                    seq.channel for seq in sequences
                )  # Find the lowest channel number
                while not nearest_strip and (active_channel >= lowest_channel):
                    for seq in sequences:
                        if (
                            seq.channel
                            == active_channel  # Check if the sequence is in the channel below
                            and abs(
                                seq.frame_final_start
                                + (seq.frame_final_end - seq.frame_final_start) / 2
                                - (
                                    active_strip.frame_final_start
                                    + (
                                        active_strip.frame_final_end
                                        - active_strip.frame_final_start
                                    )
                                    / 2
                                )
                            )
                            < nearest_distance
                        ):
                            nearest_distance = abs(
                                seq.frame_final_start
                                + (seq.frame_final_end - seq.frame_final_start) / 2
                                - (
                                    active_strip.frame_final_start
                                    + (
                                        active_strip.frame_final_end
                                        - active_strip.frame_final_start
                                    )
                                    / 2
                                )
                            )
                            nearest_strip = seq
                    active_channel -= 1
            if nearest_strip:
                nearest_strip.select = True
                context.scene.sequence_editor.active_strip = nearest_strip
            else:
                context.scene.sequence_editor.active_strip = active_strip
                active_strip.select = True
            context.scene.frame_current = (
                context.scene.sequence_editor.active_strip.frame_final_start
            )
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(SEQUENCER_OT_move_selection.bl_idname)


# Append the operator options as a submenu in SEQUENCER_MT_editor_menus
def menu_func(self, context):
    layout = self.layout
    layout.operator_menu_enum(
        SEQUENCER_OT_move_selection.bl_idname, "direction", text="Move Selection"
    )


def register():
    bpy.utils.register_class(SEQUENCER_OT_move_selection)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # Register keymap for Numpad keys
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Sequencer", space_type="SEQUENCE_EDITOR")
    kmi_up = km.keymap_items.new("sequencer.change_selection", "NUMPAD_8", "PRESS")
    kmi_up.properties.direction = "UP"
    kmi_left = km.keymap_items.new("sequencer.change_selection", "NUMPAD_4", "PRESS")
    kmi_left.properties.direction = "LEFT"
    kmi_right = km.keymap_items.new("sequencer.change_selection", "NUMPAD_6", "PRESS")
    kmi_right.properties.direction = "RIGHT"
    kmi_down = km.keymap_items.new("sequencer.change_selection", "NUMPAD_2", "PRESS")
    kmi_down.properties.direction = "DOWN"

    bpy.types.SEQUENCER_MT_select.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_move_selection)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # Unregister keymap for Numpad keys
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps["Window"]
    km.keymap_items.remove(km.keymap_items["sequencer.change_selection"])
    km.keymap_items.remove(km.keymap_items["sequencer.change_selection"])
    km.keymap_items.remove(km.keymap_items["sequencer.change_selection"])
    km.keymap_items.remove(km.keymap_items["sequencer.change_selection"])

    bpy.types.SEQUENCER_MT_select.remove(menu_func)


if __name__ == "__main__":
    register()
