"""Base plugin class for 3DEqualizer.

Note:
    3dequalizer 7.1v2 uses Python 3.7.9
    3dequalizer 8.0 uses Python 3.9

"""
from __future__ import annotations

from abc import ABCMeta

import six
from ayon_core.lib import BoolDef, EnumDef, NumberDef
from ayon_core.pipeline import (
    CreatedInstance,
    Creator,
    OptionalPyblishPluginMixin,
)


@six.add_metaclass(ABCMeta)
class EqualizerCreator(Creator):
    """Base class for creating instances in 3DEqualizer."""

    def create(self,
               product_name: str,
               instance_data: dict,
               _pre_create_data: dict):
        """Create a subset in the host application.

        Args:
            product_name (str): Name of the subset to create.
            instance_data (dict): Data of the instance to create.
            _pre_create_data (dict): Data from the pre-create step.

        Returns:
            ayon_core.pipeline.CreatedInstance: Created instance.

        """
        self.log.debug("EqualizerCreator.create")
        instance = CreatedInstance(
            self.product_type,
            product_name,
            instance_data,
            self)
        self._add_instance_to_context(instance)
        return instance

    def collect_instances(self):
        """Collect instances from the host application.

        Returns:
            list[openpype.pipeline.CreatedInstance]: List of instances.

        """
        for instance_data in self.host.get_context_data().get(
                "publish_instances", []):
            created_instance = CreatedInstance.from_existing(
                instance_data, self
            )
            self._add_instance_to_context(created_instance)

    def update_instances(self, update_list: list[dict]):
        """Update instances in the host application."""
        context = self.host.get_context_data()
        if not context.get("publish_instances"):
            context["publish_instances"] = []

        instances_by_id = {}
        for instance in context.get("publish_instances"):
            # sourcery skip: use-named-expression
            instance_id = instance.get("instance_id")
            if instance_id:
                instances_by_id[instance_id] = instance

        for instance, changes in update_list:
            new_instance_data = changes.new_value
            instance_data = instances_by_id.get(instance.id)
            # instance doesn't exist, append everything
            if instance_data is None:
                context["publish_instances"].append(new_instance_data)
                continue

            # update only changed values on instance
            for key in set(instance_data) - set(new_instance_data):
                instance_data.pop(key)
                instance_data.update(new_instance_data)

        self.host.update_context_data(context, changes=update_list)

    def remove_instances(self, instances: list[dict]):
        """Remove instances from the host application."""
        context = self.host.get_context_data()
        if not context.get("publish_instances"):
            context["publish_instances"] = []

        ids_to_remove = [
            instance.get("instance_id")
            for instance in instances
        ]
        for instance in context.get("publish_instances"):
            if instance.get("instance_id") in ids_to_remove:
                context["publish_instances"].remove(instance)

        self.host.update_context_data(context, changes={})


class ExtractScriptBase(OptionalPyblishPluginMixin):
    """Base class for extract script plugins."""

    hide_reference_frame = False
    export_uv_textures = False
    overscan_percent_width = 100
    overscan_percent_height = 100
    units = "mm"

    @classmethod
    def apply_settings(
            cls, project_settings: dict,
            system_settings: dict) -> None:  # noqa: ARG003
        """Apply settings from the configuration."""
        settings = project_settings["equalizer"]["publish"][
            "ExtractMatchmoveScriptMaya"]

        cls.hide_reference_frame = settings.get(
            "hide_reference_frame", cls.hide_reference_frame)
        cls.export_uv_textures = settings.get(
            "export_uv_textures", cls.export_uv_textures)
        cls.overscan_percent_width = settings.get(
            "overscan_percent_width", cls.overscan_percent_width)
        cls.overscan_percent_height = settings.get(
            "overscan_percent_height", cls.overscan_percent_height)
        cls.units = settings.get("units", cls.units)

    @classmethod
    def get_attribute_defs(cls) -> list:
        """Get attribute definitions for the plugin."""
        defs = super().get_attribute_defs()

        defs.extend([
            BoolDef("hide_reference_frame",
                    label="Hide Reference Frame",
                    default=cls.hide_reference_frame),
            BoolDef("export_uv_textures",
                    label="Export UV Textures",
                    default=cls.export_uv_textures),
            NumberDef("overscan_percent_width",
                      label="Overscan Width %",
                      default=cls.overscan_percent_width,
                      decimals=0,
                      minimum=1,
                      maximum=1000),
            NumberDef("overscan_percent_height",
                      label="Overscan Height %",
                      default=cls.overscan_percent_height,
                      decimals=0,
                      minimum=1,
                      maximum=1000),
            EnumDef("units",
                    ["mm", "cm", "m", "in", "ft", "yd"],
                    default=cls.units,
                    label="Units"),
            BoolDef("point_sets",
                    label="Export Point Sets",
                    default=True),
            BoolDef("export_2p5d",
                    label="Export 2.5D Points",
                    default=True),
        ])
        return defs
