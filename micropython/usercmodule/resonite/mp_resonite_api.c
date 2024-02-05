
#include "mp_resonite_api.h"

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "resonite_api.h"
#include "mp_resonite_utils.h"

// Micropython shims for the Resonite API.
// Autogenerated by generate_api.py. DO NOT EDIT.

mp_obj_t resonite__slot__root_slot() {
  resonite_refid_t outSlot;

  resonite_error_t _err = slot__root_slot(
    &outSlot);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outSlot)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_parent(mp_obj_t slot) {
  resonite_refid_t outParent;

  resonite_error_t _err = slot__get_parent(
    mp_obj_int_get_uint64_checked(slot), 
    &outParent);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outParent)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_active_user(mp_obj_t slot) {
  resonite_refid_t outUser;

  resonite_error_t _err = slot__get_active_user(
    mp_obj_int_get_uint64_checked(slot), 
    &outUser);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outUser)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_active_user_root(mp_obj_t slot) {
  resonite_refid_t outUserRoot;

  resonite_error_t _err = slot__get_active_user_root(
    mp_obj_int_get_uint64_checked(slot), 
    &outUserRoot);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outUserRoot)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_object_root(mp_obj_t slot, mp_obj_t only_explicit) {
  resonite_refid_t outObjectRoot;

  resonite_error_t _err = slot__get_object_root(
    mp_obj_int_get_uint64_checked(slot), 
    mp_obj_is_true(only_explicit) ? 1 : 0, 
    &outObjectRoot);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outObjectRoot)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_name(mp_obj_t slot) {
  char * outName;

  resonite_error_t _err = slot__get_name(
    mp_obj_int_get_uint64_checked(slot), 
    &outName);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_null_terminated_str(outName)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__set_name(mp_obj_t slot, mp_obj_t name) {

  resonite_error_t _err = slot__set_name(
    mp_obj_int_get_uint64_checked(slot), 
    mp_obj_str_get_str(name));

  mp_resonite_check_error(_err);

  mp_obj_t _outs[0] = {};


  return mp_obj_new_tuple(0, _outs);
}

mp_obj_t resonite__slot__get_num_children(mp_obj_t slot) {
  int32_t outNumChildren;

  resonite_error_t _err = slot__get_num_children(
    mp_obj_int_get_uint64_checked(slot), 
    &outNumChildren);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outNumChildren)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_child(mp_obj_t slot, mp_obj_t index) {
  resonite_refid_t outChild;

  resonite_error_t _err = slot__get_child(
    mp_obj_int_get_uint64_checked(slot), 
    (int32_t)mp_obj_get_int(index), 
    &outChild);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outChild)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_children(mp_obj_t slot) {
  resonite_buff_t outChildren;

  resonite_error_t _err = slot__get_children(
    mp_obj_int_get_uint64_checked(slot), 
    &outChildren);

  mp_resonite_check_error(_err);

  mp_obj_t outChildren__list = mp_obj_new_list(0, NULL);
  for (size_t i = 0; i < outChildren.len; i++) {
    mp_obj_list_append(outChildren__list,
      mp_obj_new_int_from_ll(((resonite_refid_t*)outChildren.ptr)[i]));
  }
  mp_obj_t _outs[1] = {
    outChildren__list};

  free(outChildren.ptr);

  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__find_child_by_name(size_t n_args, const mp_obj_t *args) {
  resonite_refid_t outChild;

  resonite_error_t _err = slot__find_child_by_name(
    mp_obj_int_get_uint64_checked(args[0]), 
    mp_obj_str_get_str(args[1]), 
    mp_obj_is_true(args[2]) ? 1 : 0, 
    mp_obj_is_true(args[3]) ? 1 : 0, 
    (int32_t)mp_obj_get_int(args[4]), 
    &outChild);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outChild)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__find_child_by_tag(mp_obj_t slot, mp_obj_t tag, mp_obj_t max_depth) {
  resonite_refid_t outChild;

  resonite_error_t _err = slot__find_child_by_tag(
    mp_obj_int_get_uint64_checked(slot), 
    mp_obj_str_get_str(tag), 
    (int32_t)mp_obj_get_int(max_depth), 
    &outChild);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outChild)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_component(mp_obj_t slot, mp_obj_t typeName) {
  resonite_refid_t outComponent;

  resonite_error_t _err = slot__get_component(
    mp_obj_int_get_uint64_checked(slot), 
    mp_obj_str_get_str(typeName), 
    &outComponent);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outComponent)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__slot__get_components(mp_obj_t slot) {
  resonite_buff_t outComponents;

  resonite_error_t _err = slot__get_components(
    mp_obj_int_get_uint64_checked(slot), 
    &outComponents);

  mp_resonite_check_error(_err);

  mp_obj_t outComponents__list = mp_obj_new_list(0, NULL);
  for (size_t i = 0; i < outComponents.len; i++) {
    mp_obj_list_append(outComponents__list,
      mp_obj_new_int_from_ll(((resonite_refid_t*)outComponents.ptr)[i]));
  }
  mp_obj_t _outs[1] = {
    outComponents__list};

  free(outComponents.ptr);

  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__component__get_type_name(mp_obj_t component) {
  char * outTypeName;

  resonite_error_t _err = component__get_type_name(
    mp_obj_int_get_uint64_checked(component), 
    &outTypeName);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_null_terminated_str(outTypeName)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__component__get_member(mp_obj_t component, mp_obj_t name) {
  resonite_type_t outType;
  resonite_refid_t outMember;

  resonite_error_t _err = component__get_member(
    mp_obj_int_get_uint64_checked(component), 
    mp_obj_str_get_str(name), 
    &outType, 
    &outMember);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[2] = {
    mp_obj_new_int_from_ll(outType), 
    mp_obj_new_int_from_ll(outMember)};


  return mp_obj_new_tuple(2, _outs);
}

mp_obj_t resonite__value__get_int(mp_obj_t refId) {
  int32_t outPtr;

  resonite_error_t _err = value__get_int(
    mp_obj_int_get_uint64_checked(refId), 
    &outPtr);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_int_from_ll(outPtr)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__value__get_float(mp_obj_t refId) {
  float outPtr;

  resonite_error_t _err = value__get_float(
    mp_obj_int_get_uint64_checked(refId), 
    &outPtr);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_float((double)outPtr)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__value__get_double(mp_obj_t refId) {
  double outPtr;

  resonite_error_t _err = value__get_double(
    mp_obj_int_get_uint64_checked(refId), 
    &outPtr);

  mp_resonite_check_error(_err);

  mp_obj_t _outs[1] = {
    mp_obj_new_float(outPtr)};


  return mp_obj_new_tuple(1, _outs);
}

mp_obj_t resonite__value__set_int(mp_obj_t refId, mp_obj_t value) {

  resonite_error_t _err = value__set_int(
    mp_obj_int_get_uint64_checked(refId), 
    (int32_t)mp_obj_get_int(value));

  mp_resonite_check_error(_err);

  mp_obj_t _outs[0] = {};


  return mp_obj_new_tuple(0, _outs);
}

mp_obj_t resonite__value__set_float(mp_obj_t refId, mp_obj_t value) {

  resonite_error_t _err = value__set_float(
    mp_obj_int_get_uint64_checked(refId), 
    (float)mp_obj_get_float(value));

  mp_resonite_check_error(_err);

  mp_obj_t _outs[0] = {};


  return mp_obj_new_tuple(0, _outs);
}

mp_obj_t resonite__value__set_double(mp_obj_t refId, mp_obj_t value) {

  resonite_error_t _err = value__set_double(
    mp_obj_int_get_uint64_checked(refId), 
    (double)mp_obj_get_float(value));

  mp_resonite_check_error(_err);

  mp_obj_t _outs[0] = {};


  return mp_obj_new_tuple(0, _outs);
}

