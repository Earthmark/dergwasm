
#ifndef __DERGWASM_C_RESONITE_API_H__
#define __DERGWASM_C_RESONITE_API_H__

#include <stdbool.h>
#include <stdint.h>

#include "resonite_api_types.h"

// C API corresponding to the Resonite API.
// Autogenerated by generate_api.py. DO NOT EDIT.

extern resonite_error_t slot__root_slot(
    resonite_refid_t* outSlot);
extern resonite_error_t slot__get_parent(
    resonite_refid_t slot, 
    resonite_refid_t* outParent);
extern resonite_error_t slot__get_active_user(
    resonite_refid_t slot, 
    resonite_refid_t* outUser);
extern resonite_error_t slot__get_active_user_root(
    resonite_refid_t slot, 
    resonite_refid_t* outUserRoot);
extern resonite_error_t slot__get_object_root(
    resonite_refid_t slot, 
    bool only_explicit, 
    resonite_refid_t* outObjectRoot);
extern resonite_error_t slot__get_name(
    resonite_refid_t slot, 
    char ** outName);
extern resonite_error_t slot__set_name(
    resonite_refid_t slot, 
    char * name);
extern resonite_error_t slot__get_num_children(
    resonite_refid_t slot, 
    int32_t* outNumChildren);
extern resonite_error_t slot__get_child(
    resonite_refid_t slot, 
    int32_t index, 
    resonite_refid_t* outChild);
extern resonite_error_t slot__get_children(
    resonite_refid_t slot, 
    int32_t* outChildListLength, 
    resonite_refid_t** outChildListData);
extern resonite_error_t slot__find_child_by_name(
    resonite_refid_t slot, 
    char * name, 
    bool match_substring, 
    bool ignore_case, 
    int32_t max_depth, 
    resonite_refid_t* outChild);
extern resonite_error_t slot__find_child_by_tag(
    resonite_refid_t slot, 
    char * tag, 
    int32_t max_depth, 
    resonite_refid_t* outChild);
extern resonite_error_t slot__get_component(
    resonite_refid_t slot, 
    char * typeName, 
    resonite_refid_t* outComponent);
extern resonite_error_t slot__get_components(
    resonite_refid_t slot, 
    int32_t* outComponentListLength, 
    resonite_refid_t** outComponentListData);
extern resonite_error_t component__get_type_name(
    resonite_refid_t component, 
    char ** outTypeName);
extern resonite_error_t component__get_member(
    resonite_refid_t component, 
    char * name, 
    resonite_type_t* outType, 
    resonite_refid_t* outMember);
extern resonite_error_t value__get_int(
    resonite_refid_t refId, 
    int32_t* outPtr);
extern resonite_error_t value__get_float(
    resonite_refid_t refId, 
    float* outPtr);
extern resonite_error_t value__get_double(
    resonite_refid_t refId, 
    double* outPtr);
extern resonite_error_t value__set_int(
    resonite_refid_t refId, 
    int32_t* inPtr);
extern resonite_error_t value__set_float(
    resonite_refid_t refId, 
    float* inPtr);
extern resonite_error_t value__set_double(
    resonite_refid_t refId, 
    double* inPtr);

#endif // __DERGWASM_C_RESONITE_API_H__
