"""Sensor platform for ETC Toll (Sri Lanka) integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CARD_NUMBER, DOMAIN
from .coordinator import EtcDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EtcSensorEntityDescription(SensorEntityDescription):
    """Describes an ETC sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[EtcSensorEntityDescription, ...] = (
    EtcSensorEntityDescription(
        key="balance",
        translation_key="balance",
        name="Balance",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="LKR",
        suggested_display_precision=2,
        icon="mdi:cash-multiple",
        value_fn=lambda data: data.get("balance"),
    ),
    EtcSensorEntityDescription(
        key="status",
        translation_key="status",
        name="Card Status",
        icon="mdi:check-decagram-outline",
        value_fn=lambda data: data.get("status"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ETC sensors based on a config entry."""
    coordinator: EtcDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EtcSensorEntity(
            coordinator=coordinator,
            card_number=entry.data[CONF_CARD_NUMBER],
            description=desc,
        )
        for desc in SENSOR_DESCRIPTIONS
    )


class EtcSensorEntity(
    CoordinatorEntity[EtcDataUpdateCoordinator], SensorEntity
):
    """Representation of an ETC Toll sensor."""

    entity_description: EtcSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EtcDataUpdateCoordinator,
        card_number: str,
        description: EtcSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._card_number = card_number
        self._attr_unique_id = f"{DOMAIN}_{card_number}_{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, card_number)},
            name=f"ETC Card {card_number}",
            manufacturer="Road Development Authority (RDA)",
            model="Expressway Electronic Toll Collection (ETC)",
            configuration_url="https://www.exway.rda.gov.lk/etconline/en/quick-topup",
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        if self.entity_description.key == "balance":
            return {
                "card_number": self._card_number,
                "balance_display": self.coordinator.data.get("balance_display"),
                "balance_cents": self.coordinator.data.get("balance_cents"),
                "status": self.coordinator.data.get("status"),
            }
        return {}

