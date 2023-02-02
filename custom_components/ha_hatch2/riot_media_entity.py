import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerDeviceClass,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)

from hatch_rest_api import RestIot
from .rest_entity import RestEntity

_LOGGER = logging.getLogger(__name__)


class RiotMediaEntity(RestEntity, MediaPlayerEntity):
    _attr_should_poll = False
    _attr_media_content_type = MediaType.MUSIC
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_media_title = None
    _attr_sound_mode = None

    def __init__(self, rest_device: RestIot):
        super().__init__(rest_device, "Media Player")
        self._attr_sound_mode_list = self.rest_device.favorite_names()
        self._attr_sound_mode = self._attr_sound_mode_list[0]
        self._attr_media_title = self._attr_sound_mode_list[0]
        self._attr_supported_features = (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.SELECT_SOUND_MODE
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
        )

    def _update_local_state(self):
        if self.platform is None:
            return
        _LOGGER.debug(f"updating state:{self.rest_device}")
        if self.rest_device.is_playing:
            self._attr_state = MediaPlayerState.PLAYING
        else:
            self._attr_state = MediaPlayerState.IDLE
        self._attr_sound_mode = self.rest_device.current_playing
        self._attr_media_title = self.rest_device.audio_track.name
        self._attr_volume_level = self.rest_device.volume / 100
        self._attr_extra_state_attributes["currently_playing"] = self._attr_sound_mode is not None
        self._attr_device_info.update(sw_version=self.rest_device.firmware_version)
        self.async_write_ha_state()

    def set_volume_level(self, volume):
        self.rest_device.set_volume(volume * 100)

    def media_play(self):
        self.rest_device.set_favorite(self._attr_sound_mode_list[0])

    def select_sound_mode(self, sound_mode: str):
        self._attr_sound_mode = sound_mode
        self._attr_media_title = sound_mode
        self.rest_device.set_favorite(sound_mode)

    def media_stop(self):
        self.rest_device.turn_off()


