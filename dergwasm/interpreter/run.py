"""Main entry point for the interpreter."""

# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=unused-argument
# pylint: disable=invalid-name

import struct
import sys
from typing import cast

from dergwasm.interpreter import binary
from dergwasm.interpreter.machine import Machine, HostFuncInstance, ModuleFuncInstance
from dergwasm.interpreter.machine_impl import MachineImpl
from dergwasm.interpreter import values
from dergwasm.interpreter.module_instance import ModuleInstance


# env.emscripten_memcpy_js
# (type (;4;) (func (param i32 i32 i32)))
def emscripten_memcpy_js(machine: Machine, dest: int, src: int, n: int) -> None:
    print(f"Called emscripten_memcpy_js({dest}, {src}, {n})")
    machine_data = machine.get_mem_data(0)
    machine_data[dest: dest + n] = machine_data[src: src + n]


# wasi_snapshot_preview1.fd_write
# (type (;5;) (func (param i32 i32 i32 i32) (result i32)))
# __wasi_errno_t __wasi_fd_write(
# __wasi_fd_t fd,
#
# /**
#  * List of scatter/gather vectors from which to retrieve data.
#  */
# const __wasi_ciovec_t *iovs,
#
# /**
#  * The length of the array pointed to by `iovs`.
#  */
# size_t iovs_len,
#
# /**
#  * The number of bytes written.
#  */
# __wasi_size_t *nwritten
# )
#
# /**
#  * A region of memory for scatter/gather writes.
#  */
# typedef struct __wasi_ciovec_t {
#     /**
#      * The address of the buffer to be written.
#      */
#     const uint8_t * buf;
#
#     /**
#      * The length of the buffer to be written.
#      */
#     __wasi_size_t buf_len;
#
# } __wasi_ciovec_t;
# See: https://wasix.org/docs/api-reference/wasi/fd_write
def fd_write(machine: Machine, fd: int, iovs: int, iovs_len: int, nwritten_ptr: int) -> int:
    print(f"Called fd_write({fd}, {iovs}, {iovs_len}, {nwritten_ptr})")
    machine_data = machine.get_mem_data(0)
    ptr = iovs
    nwritten = 0
    for i in range(iovs_len):
        buf = struct.unpack("<I", machine_data[ptr : ptr + 4])[0]
        buf_len = struct.unpack("<I", machine_data[ptr + 4 : ptr + 8])[0]
        print(f"  iovs[{i}]: buf={buf}, buf_len={buf_len}")
        if buf_len > 0:
            buf_data = machine_data[buf : buf + buf_len]
            print(f"    buf_data={buf_data}")
            s = buf_data.decode('utf-8')
            print(s)
            nwritten += buf_len
        ptr += 8
    print(f"  nwritten={nwritten}")
    struct.pack_into("<I", machine_data, nwritten_ptr, nwritten)
    return 0


def run() -> None:
    """Runs the interpreter."""
    machine_impl = MachineImpl()

    # Add all host functions to the machine.
    emscripten_memcpy_js_idx = machine_impl.add_func(
        HostFuncInstance(
            binary.FuncType([values.ValueType.I32] * 3, []), emscripten_memcpy_js
        )
    )
    fd_write_idx = machine_impl.add_func(
        HostFuncInstance(
            binary.FuncType([values.ValueType.I32] * 4, [values.ValueType.I32]),
            fd_write,
        )
    )

    module = binary.Module.from_file("F:/dergwasm/hello_world.wasm")
    print("Required imports to the module:")
    import_section = cast(binary.ImportSection, module.sections[binary.ImportSection])
    types_section = cast(binary.TypeSection, module.sections[binary.TypeSection])
    for import_ in import_section.imports:
        t = (
            types_section.types[import_.desc]
            if isinstance(import_.desc, int)
            else import_.desc
        )
        print(f"{import_.module}.{import_.name}: {t}")

    module_inst = ModuleInstance.instantiate(
        module,
        [
            # These are the imports that the module needs to access, but does not
            # provide. They must match one-to-one with the module's import specs.
            #
            # Since this is an ordered list, and we wouldn't actually know beforehand
            # what the order of imports are, ideally we would key our host functions
            # off of the name, and match them up to the import names.
            values.RefVal(values.RefValType.EXTERN_FUNC, emscripten_memcpy_js_idx),
            values.RefVal(values.RefValType.EXTERN_FUNC, fd_write_idx),
        ],
        machine_impl,
    )
    print("Exports from the module:")
    for export, val in module_inst.exports.items():
        print(f"{export}: {val}")
        if val.val_type == values.RefValType.EXTERN_FUNC:
            if val.addr is None:
                print("  = null ref")
            else:
                print(f"  = {machine_impl.get_func(val.addr).functype}")

    # print("Functions in the machine:")
    # for i, f in enumerate(machine_impl.funcs):
    #     print(f"{i}: {type(f)}: {f.functype}")
    # print("Function indexes in the module:")
    # for i, f in enumerate(module_inst.funcaddrs):
    #     ff = machine_impl.get_func(f)
    #     print(f"{i}: {f} = {type(ff)}: {ff.functype}")

    # main is (func (;3;) (type 7) (param i32 i32) (result i32)
    # Presumably int main(int argc, char *argv[]).

    addr = module_inst.exports["main"].addr
    print(f"Invoking function at machine funcaddr {addr}")
    assert addr is not None
    draw = machine_impl.get_func(addr)
    assert isinstance(draw, ModuleFuncInstance)

    machine_impl.push(values.Value(values.ValueType.I32, 0))
    machine_impl.push(values.Value(values.ValueType.I32, 0))
    machine_impl.invoke_func(addr)
    return_code = machine_impl.pop_value().intval()
    print(f"Return code: {return_code}")


if __name__ == "__main__":
    run()
