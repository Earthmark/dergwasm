
#include "resonite_api.h"

#include <stdbool.h>
#include <stdint.h>
#include <emscripten.h>

// C API corresponding to the Resonite API.
// Contains all keepalives for resonite_api.
// This file isn't needed when compiling MicroPython because MicroPython
//   uses the functions.
// Autogenerated by generate_api.py. DO NOT EDIT.

EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__root_slot(
    resonite_refid_t* outSlot) {
    return slot__root_slot(outSlot);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_parent(
    resonite_refid_t slot, 
    resonite_refid_t* outParent) {
    return slot__get_parent(slot, outParent);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_active_user(
    resonite_refid_t slot, 
    resonite_refid_t* outUser) {
    return slot__get_active_user(slot, outUser);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_active_user_root(
    resonite_refid_t slot, 
    resonite_refid_t* outUserRoot) {
    return slot__get_active_user_root(slot, outUserRoot);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_object_root(
    resonite_refid_t slot, 
    bool only_explicit, 
    resonite_refid_t* outObjectRoot) {
    return slot__get_object_root(slot, only_explicit, outObjectRoot);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_name(
    resonite_refid_t slot, 
    char ** outName) {
    return slot__get_name(slot, outName);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__set_name(
    resonite_refid_t slot, 
    char * name) {
    return slot__set_name(slot, name);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_num_children(
    resonite_refid_t slot, 
    int32_t* outNumChildren) {
    return slot__get_num_children(slot, outNumChildren);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_child(
    resonite_refid_t slot, 
    int32_t index, 
    resonite_refid_t* outChild) {
    return slot__get_child(slot, index, outChild);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_children(
    resonite_refid_t slot, 
    resonite_buff_t* outChildren) {
    return slot__get_children(slot, outChildren);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__find_child_by_name(
    resonite_refid_t slot, 
    char * name, 
    bool match_substring, 
    bool ignore_case, 
    int32_t max_depth, 
    resonite_refid_t* outChild) {
    return slot__find_child_by_name(slot, name, match_substring, ignore_case, max_depth, outChild);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__find_child_by_tag(
    resonite_refid_t slot, 
    char * tag, 
    int32_t max_depth, 
    resonite_refid_t* outChild) {
    return slot__find_child_by_tag(slot, tag, max_depth, outChild);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_component(
    resonite_refid_t slot, 
    char * typeName, 
    resonite_refid_t* outComponent) {
    return slot__get_component(slot, typeName, outComponent);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _slot__get_components(
    resonite_refid_t slot, 
    resonite_buff_t* outComponents) {
    return slot__get_components(slot, outComponents);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _component__get_type_name(
    resonite_refid_t component, 
    char ** outTypeName) {
    return component__get_type_name(component, outTypeName);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _component__get_member(
    resonite_refid_t component, 
    char * name, 
    resonite_type_t* outType, 
    resonite_refid_t* outMember) {
    return component__get_member(component, name, outType, outMember);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__get_int(
    resonite_refid_t refId, 
    int32_t* outPtr) {
    return value__get_int(refId, outPtr);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__get_float(
    resonite_refid_t refId, 
    float* outPtr) {
    return value__get_float(refId, outPtr);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__get_double(
    resonite_refid_t refId, 
    double* outPtr) {
    return value__get_double(refId, outPtr);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__set_int(
    resonite_refid_t refId, 
    int32_t value) {
    return value__set_int(refId, value);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__set_float(
    resonite_refid_t refId, 
    float value) {
    return value__set_float(refId, value);
}
EMSCRIPTEN_KEEPALIVE resonite_error_t _value__set_double(
    resonite_refid_t refId, 
    double value) {
    return value__set_double(refId, value);
}