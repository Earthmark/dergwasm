"""Generates the Micropython shims for the Resonite API."""

import enum
import json
import pathlib

HEADER_PREAMBLE = """
#ifndef __DERGWASM_MICROPYTHON_USERCMODULE_RESONITE_RESONITE_API_H__
#define __DERGWASM_MICROPYTHON_USERCMODULE_RESONITE_RESONITE_API_H__

#include "py/obj.h"
#include "py/runtime.h"

// Micropython shims for the Resonite API.
// Autogenerated by generate_api.py. DO NOT EDIT.

"""

HEADER_POSTAMBLE = """
#endif // __DERGWASM_MICROPYTHON_USERCMODULE_RESONITE_RESONITE_API_H__
"""

IMPL_PREAMBLE = """
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

"""

MODULE_PREAMBLE = """
#include "py/obj.h"
#include "py/runtime.h"

#include "mp_resonite_api.h"

#define MODULE_NAME MP_QSTR_resonitenative
#define DEF_FUN(args, name) STATIC MP_DEFINE_CONST_FUN_OBJ_ ## args(resonite__ ## name ## _obj, resonite__ ## name)
#define DEF_FUNN(args, name) STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(resonite__ ## name ## _obj, args, args, resonite__ ## name)
#define DEF_ENTRY(name) { MP_ROM_QSTR(MP_QSTR_ ## name), MP_ROM_PTR(&resonite__ ## name ## _obj) }

"""

MODULE_POSTAMBLE = """
STATIC MP_DEFINE_CONST_DICT(resonitenative_module_globals, resonitenative_module_globals_table);

const mp_obj_module_t resonitenative_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&resonitenative_module_globals,
};

MP_REGISTER_MODULE(MODULE_NAME, resonitenative_user_cmodule);
"""


def output_dir() -> pathlib.Path:
    """Gets the path to the directory where the generated files should be placed."""
    return pathlib.Path(__file__).parent.resolve()


@enum.unique
class ValueType(enum.IntEnum):
    I32 = 0x7F
    I64 = 0x7E
    F32 = 0x7D
    F64 = 0x7C
    V128 = 0x7B
    FUNCREF = 0x70
    EXTERNREF = 0x6F


class GenericType:
    base_type: str
    type_params: list["GenericType"]

    def __init__(self, base_type: str, type_params: list["GenericType"] | None = None):
        self.base_type = base_type
        self.type_params = type_params if type_params is not None else []

    def is_output(self) -> bool:
        return self.base_type == "Output"

    @staticmethod
    def parse_generic_type(s: str) -> "GenericType":
        """Helper function to split the string by commas, considering nested generics."""

        def split_type_params(s: str) -> list[str]:
            params: list[str] = []
            bracket_level = 0
            current = ""
            for char in s:
                if char == "," and bracket_level == 0:
                    params.append(current)
                    current = ""
                else:
                    if char == "<":
                        bracket_level += 1
                    elif char == ">":
                        bracket_level -= 1
                    current += char
            if current:
                params.append(current)
            return params

        # Base case: no type parameters
        if "<" not in s:
            return GenericType(s)

        # Recursive case: parse type parameters
        base_type, rest = s.split("<", 1)
        type_params_str = rest[:-1]  # Remove the closing '>'
        type_params = [
            GenericType.parse_generic_type(tp.strip())
            for tp in split_type_params(type_params_str)
        ]
        return GenericType(base_type, type_params)

    def __repr__(self) -> str:
        if not self.type_params:
            return self.base_type
        return f"{self.base_type}:({', '.join(map(str, self.type_params))})"


PY_TO_WASM: dict[ValueType, str] = {
    ValueType.I32: "(int32_t)mp_obj_get_int",
    ValueType.I64: "mp_obj_int_get_int64_checked",
    ValueType.F32: "(float)mp_obj_get_float",
    ValueType.F64: "(double)mp_obj_get_float",
}

WASM_TO_PY: dict[ValueType, str] = {
    ValueType.I32: "mp_obj_new_int_from_ll",
    ValueType.I64: "mp_obj_new_int_from_ll",
    ValueType.F32: "mp_obj_new_float",
    ValueType.F64: "mp_obj_new_float",
}

class Main:
    """The main class for the Micropython API generator."""

    @staticmethod
    def wasm_to_c(cc_type: GenericType) -> str:
        """Converts a Dergwasm type to a C type."""
        cc_type_str = cc_type.base_type
        if cc_type_str == "int":
            return "int32_t"
        if cc_type_str == "uint":
            return "uint32_t"
        if cc_type_str == "long":
            return "int64_t"
        if cc_type_str == "ulong":
            return "uint64_t"
        if cc_type_str == "float":
            return "float"
        if cc_type_str == "double":
            return "double"
        if cc_type_str == "bool":
            return "bool"
        if cc_type_str == "WasmRefID":
            return "resonite_refid_t"
        if cc_type_str == "Ptr":
            return Main.wasm_to_c(cc_type.type_params[0]) + "*"
        if cc_type_str == "Output":
            return Main.wasm_to_c(cc_type.type_params[0]) + "*"
        if cc_type_str == "WasmArray":
            return Main.wasm_to_c(cc_type.type_params[0]) + "*"
        if cc_type_str == "NullTerminatedString":
            return "char *"
        if cc_type_str == "ResoniteError":
            return "resonite_error_t"
        if cc_type_str == "ResoniteType":
            return "resonite_type_t"
        if cc_type_str == "Buff":
            return "resonite_buff_t"
        raise ValueError(f"Unknown type: {cc_type_str}")

    @staticmethod
    def py_to_wasm(cc_type: GenericType, val: str) -> str:
        """Converts a Python value to a Dergwasm value, for arguments."""
        cc_type_str = str(cc_type)
        if cc_type_str == "int":
            return f"(int32_t)mp_obj_get_int({val})"
        if cc_type_str == "uint":
            return f"(uint32_t)mp_obj_get_int({val})"
        if cc_type_str == "long":
            return f"mp_obj_int_get_int64_checked({val})"
        if cc_type_str == "ulong":
            return f"mp_obj_int_get_uint64_checked({val})"
        if cc_type_str == "float":
            return f"(float)mp_obj_get_float({val})"
        if cc_type_str == "double":
            return f"(double)mp_obj_get_float({val})"
        if cc_type_str == "bool":
            return f"mp_obj_is_true({val}) ? 1 : 0"
        if cc_type_str.startswith("WasmRefID"):
            return f"mp_obj_int_get_uint64_checked({val})"
        if cc_type_str.startswith("Ptr"):
            return f"(int32_t)mp_obj_get_int({val})"
        if cc_type_str == "NullTerminatedString":
            return f"mp_obj_str_get_str({val})"
        raise ValueError(f"Unknown type: {cc_type_str}")

    @staticmethod
    def wasm_to_py(cc_type: GenericType, val: str) -> str:
        """Converts a Dergwasm value to a Python value, for return values."""
        cc_type_str = str(cc_type)
        if cc_type_str in [
            "int",
            "uint",
            "long",
            "ulong",
            "ResoniteError",
            "ResoniteType",
        ]:
            return f"mp_obj_new_int_from_ll({val})"
        if cc_type_str == "float":
            return f"mp_obj_new_float((double){val})"
        if cc_type_str == "double":
            return f"mp_obj_new_float({val})"
        if cc_type_str == "bool":
            return f"mp_obj_new_bool({val})"
        if cc_type_str.startswith("WasmRefID"):
            return f"mp_obj_new_int_from_ll({val})"
        if cc_type_str.startswith("Ptr"):
            return f"mp_obj_new_int_from_ll({val})"
        if cc_type_str == "NullTerminatedString":
            return f"mp_obj_new_null_terminated_str({val})"
        if cc_type_str == "Buff":
            return f"<FIXME>({val})"
        raise ValueError(f"Unknown type: {cc_type_str}")

    def get_api_data(self) -> list[dict]:
        """Gets the API data from resonite_api.json."""
        with open("resonite_api.json", "r", encoding="UTF8") as f:
            data = json.load(f)

        for item in data:
            for p in item["Parameters"]:
                p["GenericType"] = GenericType.parse_generic_type(p["CSType"])
                p["ValueTypes"] = [ValueType(t) for t in p["Types"]]

        return data

    def generate_header(self) -> None:
        """Generates the mp_resonite_api.h file."""

        data = self.get_api_data()

        generated_filename = output_dir() / "mp_resonite_api.h"
        with open(generated_filename, "w", encoding="UTF8") as f:
            f.write(HEADER_PREAMBLE)
            for item in data:
                params = [
                    f'mp_obj_t {param["Name"]}'
                    for param in item["Parameters"]
                    if not param["GenericType"].is_output()
                ]

                f.write(f'extern mp_obj_t resonite__{item["Name"]}(')
                if len(params) < 4:
                    f.write(", ".join(params))
                else:
                    f.write("size_t n_args, const mp_obj_t *args")
                f.write(");\n")
            f.write(HEADER_POSTAMBLE)

    def generate_impl(self) -> None:
        """Generates the mp_resonite_api.c file."""

        data = self.get_api_data()

        generated_filename = output_dir() / "mp_resonite_api.c"
        with open(generated_filename, "w", encoding="UTF8") as f:
            f.write(IMPL_PREAMBLE)
            for item in data:
                params = item["Parameters"]
                in_params = [p for p in params if not p["GenericType"].is_output()]
                out_params = [p for p in params if p["GenericType"].is_output()]

                arglist = [f'mp_obj_t {p["Name"]}' for p in in_params]

                f.write(f'mp_obj_t resonite__{item["Name"]}(')
                if len(in_params) < 4:
                    f.write(", ".join(arglist))
                else:
                    f.write("size_t n_args, const mp_obj_t *args")
                f.write(") {\n")

                # Outputs get local vars.
                for p in out_params:
                    c_type = self.wasm_to_c(p["GenericType"])
                    c_type = c_type[:-1]  # Remove the trailing '*'
                    f.write(f"  {c_type} {p['Name']};\n")
                f.write("\n")
                f.write(f'  resonite_error_t _err = {item["Name"]}(')

                # Write the arguments to the native call.
                call_args: list[str] = []
                in_param_num = -1
                for p in params:
                    if not p["GenericType"].is_output():
                        in_param_num += 1
                    argname = (
                        p["Name"] if len(in_params) < 4 else f"args[{in_param_num}]"
                    )
                    if p["GenericType"].is_output():
                        converted = f"&{p['Name']}"
                    else:
                        converted = self.py_to_wasm(p["GenericType"], argname)
                    call_args.append(f"\n    {converted}")
                f.write(f'{", ".join(call_args)});\n\n')

                # If there was an error, throw an exception.
                f.write("  mp_resonite_check_error(_err);\n\n")

                # Any lists that were returned need to be converted to Python lists.
                ps = iter(out_params)
                for p in ps:
                    generic_type = p["GenericType"].type_params[0]
                    if generic_type.base_type != "Buff":
                        continue

                    # Get the type this is an array of.
                    generic_type = generic_type.type_params[0]
                    c_type = self.wasm_to_c(generic_type)
                    converted = self.wasm_to_py(generic_type,
                                                f"(({c_type}*){p['Name']}.ptr)[i]")

                    # Get the length of the array.
                    len_name = f"{p['Name']}.len"

                    f.write(
                        f'  mp_obj_t {p["Name"]}__list = mp_obj_new_list(0, NULL);\n'
                    )
                    f.write(f"  for (size_t i = 0; i < {len_name}; i++) {{\n")
                    f.write(f'    mp_obj_list_append({p["Name"]}__list,\n')
                    f.write(f"      {converted});\n")
                    f.write("  }\n")

                # The return value is always a tuple.
                out_elements: list[str] = []

                for p in out_params:
                    # This is, by definition, an Output<T>, so get T.
                    generic_type = p["GenericType"].type_params[0]
                    if generic_type.base_type == "Buff":
                        converted = f"{p['Name']}__list"
                    else:
                        converted = self.wasm_to_py(generic_type, p["Name"])
                    out_elements.append(f"\n    {converted}")
                out_count = len(out_elements)

                f.write(f"  mp_obj_t _outs[{out_count}] = {{")
                f.write(", ".join(out_elements))
                f.write("};\n")
                f.write("\n")

                # Now we free anything we need to free.
                for p in params:
                    if not p["GenericType"].is_output():
                        continue
                    generic_type = p["GenericType"].type_params[0]
                    if generic_type.base_type == "Buff":
                        f.write(f"  free({p['Name']}.ptr);\n")
                f.write("\n")

                f.write(f"  return mp_obj_new_tuple({out_count}, _outs);\n")
                f.write("}\n\n")

            f.flush()

    def generate_module(self) -> None:
        """Generates the mp_resonite.c file."""

        data = self.get_api_data()

        generated_filename = output_dir() / "mp_resonite.c"
        with open(generated_filename, "w", encoding="UTF8") as f:
            f.write(MODULE_PREAMBLE)

            for item in data:
                params = item["Parameters"]
                num_in_params = len(
                    [
                        f'mp_obj_t {p["Name"]}'
                        for p in params
                        if not p["GenericType"].is_output()
                    ]
                )
                if num_in_params < 4:
                    f.write("DEF_FUN")
                else:
                    f.write("DEF_FUNN")
                f.write(f"({num_in_params}, {item['Name']});\n")

            f.write(
                "STATIC const mp_rom_map_elem_t resonitenative_module_globals_table[] = {\n"
            )
            f.write(
                "    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MODULE_NAME) },\n"
            )

            for item in data:
                f.write(f"    DEF_ENTRY({item['Name']}),\n")

            f.write("};\n")

            f.write(MODULE_POSTAMBLE)

    def main(self) -> int:
        """Generates all the shim files for the Python API."""
        self.generate_header()
        self.generate_impl()
        self.generate_module()
        return 0
