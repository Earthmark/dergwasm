// Contains all keepalives for resonite_api.

#include "resonite_api.h"

#include <stdint.h>
#include <emscripten.h>

EMSCRIPTEN_KEEPALIVE void _slot__root_slot(resonite_slot_refid_t* slot_id) {
	slot__root_slot(slot_id);
}

EMSCRIPTEN_KEEPALIVE void _slot__get_object_root(
	resonite_slot_refid_t slot_id, int only_explicit, resonite_slot_refid_t* object_root_id) {
	slot__get_object_root(slot_id, only_explicit, object_root_id);
}

EMSCRIPTEN_KEEPALIVE void _slot__get_parent(
    resonite_slot_refid_t slot_id, resonite_slot_refid_t* parent_slot_id) {
    slot__get_parent(slot_id, parent_slot_id);
}

EMSCRIPTEN_KEEPALIVE char* _slot__get_name(resonite_slot_refid_t slot_id) {
	return slot__get_name(slot_id);
}
