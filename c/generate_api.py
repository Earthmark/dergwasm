"""Generates the C API corresponding to the Resonite API."""

import json
import sys

HEADER_PREAMBLE = """
#ifndef __DERGWASM_C_RESONITE_API_H__
#define __DERGWASM_C_RESONITE_API_H__

#include <stdbool.h>
#include <stdint.h>

#include "resonite_api_types.h"

// C API corresponding to the Resonite API.
// Autogenerated by generate_api.py. DO NOT EDIT.

"""

HEADER_POSTAMBLE = """
#endif // __DERGWASM_C_RESONITE_API_H__
"""

IMPL_PREAMBLE = """
#include "resonite_api.h"

#include <stdbool.h>
#include <stdint.h>
#include <emscripten.h>

// C API corresponding to the Resonite API.
// Contains all keepalives for resonite_api.
// This file isn't needed when compiling MicroPython because MicroPython
//   uses the functions.
// Autogenerated by generate_api.py. DO NOT EDIT.

"""


class GenericType:
    base_type: str
    type_params: list["GenericType"]

    def __init__(self, base_type: str, type_params: list["GenericType"] | None = None):
        self.base_type = base_type
        self.type_params = type_params if type_params is not None else []

    @staticmethod
    def parse_generic_type(s: str) -> "GenericType":
        # Helper function to split the string by commas, considering nested generics
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


class Main:
    def __init__(self) -> None:
        pass

    @staticmethod
    def wasm_to_c(cc_type: GenericType) -> str:
        """Converts a Dergwasm type to a C type, for return values."""
        cc_type_str = str(cc_type)
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
        if cc_type_str.startswith("WasmRefID"):
            return "resonite_refid_t"
        if cc_type_str.startswith("Ptr"):
            return "void *"
        if cc_type_str == "NullTerminatedString":
            return "char *"
        if cc_type_str == "ResoniteError":
            return "int32_t"
        raise ValueError(f"Unknown type: {cc_type_str}")

    def generate_header(self) -> None:
        with open("resonite_api.json", "r", encoding="UTF8") as f:
            data = json.load(f)

        with open("c/resonite_api.h", "w", encoding="UTF8") as f:
            f.write(HEADER_PREAMBLE)
            for item in data:
                if len(item["Returns"]) == 0:
                    f.write(f'extern void {item["Name"]}(')
                else:
                    ret_generic_type = GenericType.parse_generic_type(
                        item["Returns"][0]["CSType"]
                    )
                    converted = self.wasm_to_c(ret_generic_type)
                    f.write(f'extern {converted} {item["Name"]}(')

                call_params: list[str] = []
                for param in item["Parameters"]:
                    generic_type = GenericType.parse_generic_type(param["CSType"])
                    converted = self.wasm_to_c(generic_type)
                    call_params.append(f"\n    {converted} {param['Name']}")
                f.write(", ".join(call_params))
                f.write(");\n")
            f.write(HEADER_POSTAMBLE)

    def generate_impl(self) -> None:
        with open("resonite_api.json", "r", encoding="UTF8") as f:
            data = json.load(f)

        with open("c/resonite_api.c", "w", encoding="UTF8") as f:
            f.write(IMPL_PREAMBLE)
            for item in data:
                if len(item["Returns"]) == 0:
                    f.write(f'EMSCRIPTEN_KEEPALIVE void _{item["Name"]}(')
                else:
                    ret_generic_type = GenericType.parse_generic_type(
                        item["Returns"][0]["CSType"]
                    )
                    converted = self.wasm_to_c(ret_generic_type)
                    f.write(f'EMSCRIPTEN_KEEPALIVE {converted} _{item["Name"]}(')

                call_params: list[str] = []
                for param in item["Parameters"]:
                    generic_type = GenericType.parse_generic_type(param["CSType"])
                    converted = self.wasm_to_c(generic_type)
                    call_params.append(f"\n    {converted} {param['Name']}")
                f.write(", ".join(call_params))
                f.write(") {\n")

                f.write("    ")
                if len(item["Returns"]) != 0:
                    f.write("return ")
                f.write(f"{item['Name']}(")
                f.write(", ".join([param["Name"] for param in item["Parameters"]]))
                f.write(");\n")
                f.write("}\n")

    def generate_js(self) -> None:
        with open("resonite_api.json", "r", encoding="UTF8") as f:
            data = json.load(f)

        with open("c/resonite_api.js", "w", encoding="UTF8") as f:
            for item in data:
                f.write(
                    f'mergeInto(LibraryManager.library, {{ {item["Name"]}: function () {{ }} }});\n'
                )

    def main(self) -> int:
        self.generate_header()
        self.generate_impl()
        self.generate_js()
        return 0


if __name__ == "__main__":
    sys.exit(Main().main())