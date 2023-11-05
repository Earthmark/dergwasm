"""Parsing of the binary format of a module."""

# pytype: disable=too-many-return-statements

from __future__ import annotations  # For PEP563 - postponed evaluation of annotations

import abc
import binascii
import dataclasses
from io import BytesIO
from typing import BinaryIO, Type

import leb128

from dergwasm.interpreter import insn
from dergwasm.interpreter import values


def _read_byte(f: BytesIO) -> int:
    """Reads a byte from the data stream.

    Raises:
        EOFError: upon reaching end of stream.
    """
    try:
        return f.read(1)[0]
    except IndexError as e:
        raise EOFError from e


def _read_value_type(f: BytesIO) -> values.ValueType:
    """Reads a value type from the data stream.

    Raises:
        EOFError: upon reaching end of stream.
    """
    return values.ValueType(_read_byte(f))


def _read_unsigned_int(f: BytesIO) -> int:
    """Reads an LEB128-encoded int from the data stream.

    Raises:
        EOFError: upon reaching end of stream.
    """
    try:
        return leb128.u.decode_reader(f)[0]
    except IndexError as e:
        raise EOFError from e


def _read_string(f: BytesIO) -> str:
    """Reads a string from the data stream.

    Raises:
        EOFError: upon reaching end of stream.
    """
    name_size = _read_unsigned_int(f)
    return f.read(name_size).decode("utf-8")


@dataclasses.dataclass
class ExternalType:
    """The base class for external types."""


@dataclasses.dataclass
class FuncType(ExternalType):
    """The type of a function."""

    parameters: list[values.ValueType]
    results: list[values.ValueType]

    @staticmethod
    def read(f: BytesIO) -> FuncType:
        """Reads and returns a FuncType.

        Returns:
            The FuncType read.

        Raises:
            EOFError: upon reaching end of file.
        """
        tag = _read_byte(f)
        if tag != 0x60:
            raise ValueError(f"Expected 0x60 tag for functype, but got {tag:02X}")
        num_parameters = _read_unsigned_int(f)
        parameters = [_read_value_type(f) for _ in range(num_parameters)]
        num_results = _read_unsigned_int(f)
        results = [_read_value_type(f) for _ in range(num_results)]
        return FuncType(parameters, results)

    def __repr__(self) -> str:
        return f"FuncType({self.parameters}, {self.results})"


@dataclasses.dataclass
class TableType(ExternalType):
    """The type of a table."""

    reftype: values.ValueType  # can only be FUNCREF or EXTERNREF
    limits: values.Limits

    @staticmethod
    def read(f: BytesIO) -> TableType:
        """Reads and returns a TableType."""
        reftype = values.ValueType(_read_byte(f))
        tag = _read_byte(f)
        min_limit = _read_unsigned_int(f)
        if tag == 0x00:
            max_limit = None
        elif tag == 0x01:
            max_limit = _read_unsigned_int(f)
        else:
            raise ValueError(f"Unknown tabletype limit tag {tag:02X}")
        return TableType(reftype, values.Limits(min_limit, max_limit))

    def __repr__(self) -> str:
        return f"TableType({self.reftype}, {self.limits.min}, {self.limits.max})"


@dataclasses.dataclass
class MemType(ExternalType):
    """The type of a memory."""

    limits: values.Limits

    @staticmethod
    def read(f: BytesIO) -> MemType:
        """Reads and returns a MemType."""
        tag = _read_byte(f)
        min_limit = _read_unsigned_int(f)
        if tag == 0x00:
            max_limit = None
        elif tag == 0x01:
            max_limit = _read_unsigned_int(f)
        else:
            raise ValueError(f"Unknown memtype limit tag {tag:02X}")
        return MemType(values.Limits(min_limit, max_limit))

    def __repr__(self) -> str:
        return f"MemType({self.limits.min}, {self.limits.max})"


@dataclasses.dataclass
class GlobalType(ExternalType):
    """The type of a global."""

    value_type: values.ValueType
    mutable: bool

    @staticmethod
    def read(f: BytesIO) -> GlobalType:
        """Reads and returns a GlobalType."""
        value_type = values.ValueType(_read_byte(f))
        mutable = bool(_read_byte(f))
        return GlobalType(value_type, mutable)


@dataclasses.dataclass
class Import:
    """An import.

    Each import is labeled by a two-level name space, consisting of a module name and
    a name for an entity within that module. Importable definitions are functions,
    tables, memories, and globals. Each import is specified by a descriptor with a
    respective type that a definition provided during instantiation is required to
    match.

    Every import defines an index in the respective index space. In each index space,
    the indices of imports go before the first index of any definition contained in the
    module itself (what even does this mean).
    """

    module: str
    name: str
    # The int type will be replaced by FuncType after we fix up the module after reading
    # it all in.
    desc: int | FuncType | TableType | MemType | GlobalType

    @staticmethod
    def read(f: BytesIO) -> Import:
        """Reads and returns an Import.

        `desc` is the descriptor. If it's an int, it's an index into the FuncSection
        `types` list.

        Returns:
            The Import read.

        Raises:
            ValueError: upon encountering a bad import desc tag.
        """
        module = _read_string(f)
        name = _read_string(f)
        tag = _read_byte(f)
        if tag == 0x00:
            desc = _read_unsigned_int(f)
        elif tag == 0x01:
            desc = TableType.read(f)
        elif tag == 0x02:
            desc = MemType.read(f)
        elif tag == 0x03:
            desc = GlobalType.read(f)
        else:
            raise ValueError(f"Unknown import desc tag {tag:02X}")

        return Import(module, name, desc)

    def __repr__(self) -> str:
        return f"Import({self.module}:{self.name}, {self.desc})"


@dataclasses.dataclass
class Export:
    """An export."""

    name: str
    desc_type: Type[FuncType | TableType | MemType | GlobalType]
    desc_idx: int  # The index into the respective section of the given type.

    @staticmethod
    def read(f: BytesIO) -> Export:
        """Reads and returns an Export.

        Returns:
            The Export read.

        Raises:
            ValueError: upon encountering a bad export desc tag.
        """
        name = _read_string(f)
        tag = _read_byte(f)
        if tag > 3:
            raise ValueError(f"Unknown import desc tag {tag:02X}")
        desc_type = [FuncType, TableType, MemType, GlobalType][tag]
        desc_idx = _read_unsigned_int(f)
        return Export(name, desc_type, desc_idx)


@dataclasses.dataclass
class Table:
    """A table specification.

    The initial contents of a table is uninitialized. Element segments can be used to
    initialize a subrange of a table from a static vector of elements.
    """

    table_type: TableType

    @staticmethod
    def read(f: BytesIO) -> Table:
        """Reads and returns a Table."""
        return Table(TableType.read(f))


@dataclasses.dataclass
class Mem:
    """A memory specification."""

    mem_type: MemType

    @staticmethod
    def read(f: BytesIO) -> Mem:
        """Reads and returns a Mem."""
        return Mem(MemType.read(f))


@dataclasses.dataclass
class ElementSegment:
    """An element segment specification.

    Element segments are used to initialize sections of tables. The elements of tables
    are always references (either FUNCREF or EXTERNREF).
    """

    elem_type: values.ValueType

    # The presence of expr indicates this is a "declarative" or "active" element
    # instead of a "passive" element.
    offset_expr: list[insn.Instruction] | None = None
    tableidx: int | None = None  # Only present for active elements.

    # These are mutually exclusive.
    elem_indexes: list[int] | None = None
    elem_exprs: list[list[insn.Instruction]] | None = None

    def size(self) -> int:
        """Returns the size of the element segment."""
        if self.elem_indexes is not None:
            return len(self.elem_indexes)
        if self.elem_exprs is not None:
            return len(self.elem_exprs)
        raise ValueError(
            "Element segment is not defined correctly: no indexes or exprs."
        )

    def is_active(self) -> bool:
        """Returns whether this is an active element segment."""
        return self.tableidx is not None

    def is_declarative(self) -> bool:
        """Returns whether this is a declarative element segment."""
        return not self.is_active() and self.offset_expr is not None

    def is_passive(self) -> bool:
        """Returns whether this is a passive element segment."""
        return not self.is_active() and self.offset_expr is None

    @staticmethod
    def read(f: BytesIO) -> ElementSegment:
        """Reads and returns an ElementSegment."""
        desc_idx = _read_unsigned_int(f)

        if desc_idx == 0x00:
            # A table of funcrefs at table 0, with an offset.
            tableidx = 0
            offset_expr = read_expr(f)
            elem_type = values.ValueType.FUNCREF
            elem_indexes = [
                _read_unsigned_int(f)
                for _ in range(_read_unsigned_int(f))
            ]
            return ElementSegment(
                elem_type=elem_type,
                tableidx=tableidx,
                offset_expr=offset_expr,
                elem_indexes=elem_indexes,
            )

        if desc_idx == 0x01:
            # A table of indexes of a given type.
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_indexes = [
                _read_unsigned_int(f)
                for _ in range(_read_unsigned_int(f))
            ]
            return ElementSegment(elem_type=elem_type, elem_indexes=elem_indexes)

        if desc_idx == 0x02:
            # A table of indexes of a given type at a specific tableidx and offset.
            tableidx = _read_unsigned_int(f)
            offset_expr = read_expr(f)
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_indexes = [
                _read_unsigned_int(f)
                for _ in range(_read_unsigned_int(f))
            ]
            return ElementSegment(
                elem_type=elem_type,
                tableidx=tableidx,
                offset_expr=offset_expr,
                elem_indexes=elem_indexes,
            )

        if desc_idx == 0x03:
            # A table of indexes of a given type.
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_indexes = [
                _read_unsigned_int(f)
                for _ in range(_read_unsigned_int(f))
            ]
            return ElementSegment(elem_type=elem_type, elem_indexes=elem_indexes)

        if desc_idx == 0x04:
            # A table of funcrefs given by exprs at table 0, with an offset.
            tableidx = 0
            offset_expr = read_expr(f)
            elem_type = values.ValueType.FUNCREF
            elem_exprs = [read_expr(f) for _ in range(_read_unsigned_int(f))]
            return ElementSegment(
                elem_type=elem_type,
                tableidx=tableidx,
                offset_expr=offset_expr,
                elem_exprs=elem_exprs,
            )

        if desc_idx == 0x05:
            # A table of indexes of a given type, given by exprs.
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_exprs = [read_expr(f) for _ in range(_read_unsigned_int(f))]
            return ElementSegment(
                elem_type=elem_type,
                elem_exprs=elem_exprs,
            )

        if desc_idx == 0x06:
            # A table of funcrefs given by exprs at a specific table, with an offset.
            tableidx = _read_unsigned_int(f)
            offset_expr = read_expr(f)
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_exprs = [read_expr(f) for _ in range(_read_unsigned_int(f))]
            return ElementSegment(
                elem_type=elem_type,
                tableidx=tableidx,
                offset_expr=offset_expr,
                elem_exprs=elem_exprs,
            )

        if desc_idx == 0x07:
            # A table of indexes of a given type, given by exprs.
            elem_type = values.ValueType(_read_unsigned_int(f))
            elem_exprs = [read_expr(f) for _ in range(_read_unsigned_int(f))]
            return ElementSegment(
                elem_type=elem_type,
                elem_exprs=elem_exprs,
            )

        raise ValueError(f"Unknown table element segment type tag {desc_idx:02X}")


def flatten_instructions(
    insns: list[insn.Instruction], pc: int
) -> list[insn.Instruction]:
    """Flattens a list of instructions.

    This is used to flatten out the instructions in a code section so we can compute
    instruction program counter labels.

    Every instruction has a continuation_pc. For all instructions except BLOCK, LOOP,
    and IF, this is the PC of the next instruction to execute. For BLOCK and LOOP,
    it is the PC to jump to when breaking out (i.e. if a BR 0 were to be executed).

    IF instructions have two continuations. The first is the PC just after the END
    instruction, as usual with blocks. The second is the else_continuation_pc, and
    is the PC just after the ELSE instruction, if there is one, otherwise the PC
    just after the END instruction.

    When an ELSE instruction is encountered, its continuation is the PC just after
    the END instruction.

    The continuation for BR, BR_IF, BR_TABLE, instructions are irrelevant. They just
    use the continuation_pc stored in the label they go to.

    The continuation for RETURN is irrelevant.
    """
    flattened_instructions = []
    for i in insns:
        i.else_continuation_pc = 0

        if i.instruction_type == insn.InstructionType.BLOCK:
            assert isinstance(i.operands[0], insn.Block)
            block_insns = [i]
            block_insns.extend(flatten_instructions(i.operands[0].instructions, pc + 1))
            i.operands[0].instructions = []
            flattened_instructions.extend(block_insns)
            pc += len(block_insns)
            # Where to go on breakout.
            i.continuation_pc = pc

        elif i.instruction_type == insn.InstructionType.LOOP:
            assert isinstance(i.operands[0], insn.Block)
            block_insns = [i]
            block_insns.extend(flatten_instructions(i.operands[0].instructions, pc + 1))
            i.operands[0].instructions = []
            i.operands[0].else_instructions = []
            flattened_instructions.extend(block_insns)
            # Where to go on breakout.
            i.continuation_pc = pc
            pc += len(block_insns)

        elif i.instruction_type == insn.InstructionType.IF:
            assert isinstance(i.operands[0], insn.Block)
            block_insns = [i]

            # Ends in END or ELSE.
            # continuation_pc = END + 1
            # If END, else_continuation_pc = END + 1.
            # IF ELSE, else_continuation_pc = ELSE + 1.
            true_insns = flatten_instructions(i.operands[0].instructions, pc + 1)
            i.operands[0].instructions = []
            pc += len(true_insns) + 1
            i.else_continuation_pc = pc

            false_insns = flatten_instructions(i.operands[0].else_instructions, pc)
            i.operands[0].else_instructions = []
            pc += len(false_insns)
            i.continuation_pc = pc

            if true_insns[-1].instruction_type == insn.InstructionType.ELSE:
                true_insns[-1].continuation_pc = pc

            block_insns.extend(true_insns)
            block_insns.extend(false_insns)
            flattened_instructions.extend(block_insns)

        else:
            flattened_instructions.append(i)
            pc += 1
            i.continuation_pc = pc

    return flattened_instructions


@dataclasses.dataclass
class Code:
    """A code specification."""

    local_vars: list[tuple[int, values.ValueType]]  # How many of each type of local.
    insns: list[insn.Instruction]

    @staticmethod
    def read(f: BytesIO) -> Code:
        """Reads and returns a Code."""
        # code size is used only for validation.
        _ = _read_unsigned_int(f)
        num_locals = _read_unsigned_int(f)
        local_vars = [
            (_read_unsigned_int(f), values.ValueType(_read_byte(f)))
            for _ in range(num_locals)
        ]
        insns = []
        while True:
            instruction = insn.Instruction.read(f)
            insns.append(instruction)
            if instruction.instruction_type == insn.InstructionType.END:
                break

        # Now we need to flatten out the instructions so we can compute instruction
        # program counter labels.

        return Code(local_vars, flatten_instructions(insns, 0))

    def __repr__(self) -> str:
        return "".join([i.to_str(0) for i in self.insns])


def read_expr(f: BytesIO) -> list[insn.Instruction]:
    """Reads an expression: a list of instructions terminated by an end instruction.

    The returned list is flattened.
    """
    insns = []
    while True:
        instruction = insn.Instruction.read(f)
        insns.append(instruction)
        if instruction.instruction_type == insn.InstructionType.END:
            break
    return flatten_instructions(insns, 0)


@dataclasses.dataclass
class Func:
    """A function specification."""

    typeidx: int
    local_vars: list[values.ValueType]
    body: list[insn.Instruction]


@dataclasses.dataclass
class Data:
    """A data segment.

    The initial contents of a memory are zero bytes. Data segments can be used to
    initialize a range of memory from a static vector of bytes.

    A passive (not active) data segment's contents can be copied into a memory using
    the memory.init instruction.

    An active data segment copies its contents into a memory during instantiation, as
    specified by a memory index and a constant expression defining an offset into that
    memory.
    """

    is_active: bool
    memidx: int
    offset: list[insn.Instruction] | None
    data: bytes

    @staticmethod
    def read(f: BytesIO) -> Data:
        """Reads and returns a Data."""
        tag = _read_unsigned_int(f)
        memidx = 0
        offset = None
        is_active = False

        if tag == 0x00:
            is_active = True
            offset = read_expr(f)
        elif tag == 0x02:
            is_active = True
            memidx = _read_unsigned_int(f)
            offset = read_expr(f)

        data_size = _read_unsigned_int(f)
        data = f.read(data_size)
        return Data(is_active, memidx, offset, data)


@dataclasses.dataclass
class Global:
    """A global variable specification."""

    global_type: GlobalType
    init: list[insn.Instruction]

    @staticmethod
    def read(f: BytesIO) -> Global:
        """Reads and returns a Global."""
        global_type = GlobalType.read(f)
        init = read_expr(f)
        return Global(global_type, init)


class ModuleSection(abc.ABC):
    """Base class for module sections."""

    @staticmethod
    @abc.abstractmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a module section.

        Returns:
            The module section read.
        """


@dataclasses.dataclass
class CustomSection(ModuleSection):
    """A custom section.

    Custom sections are for debugging information or third-party extensions, and are
    ignored by the WebAssembly semantics. Their contents consist of a name further
    identifying the custom section, followed by an uninterpreted sequence of bytes for
    custom use.
    """

    name: str
    data: bytes

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        name_len = _read_unsigned_int(f)
        name = f.read(name_len).decode("utf-8")
        data_len = _read_unsigned_int(f)
        data = f.read(data_len)
        print(f"Read custom section {name}: {data}")
        return CustomSection(name, data)


@dataclasses.dataclass
class TypeSection(ModuleSection):
    """A type section.

    Contains a list of function types that represent the types component of a module.
    All function types used in a module must be defined in this component. They are
    referenced by type indices.
    """

    types: list[FuncType]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a type section."""
        num_types = _read_unsigned_int(f)
        types = [FuncType.read(f) for _ in range(num_types)]
        print(f"Read types: {types}")
        return TypeSection(types)


@dataclasses.dataclass
class ImportSection(ModuleSection):
    """An imports section.

    Contains a list of imports that represent the imports component of a module. Imports
    are required for instantiation.

    In each index space, the indices of imports go before the first index of any
    definition contained in the module itself.
    """

    imports: list[Import]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns an imports section."""
        num_imports = _read_unsigned_int(f)
        imports = [Import.read(f) for _ in range(num_imports)]
        print(f"Read imports: {imports}")
        return ImportSection(imports)


@dataclasses.dataclass
class FunctionSection(ModuleSection):
    """A function section."""

    funcs: list[Func]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a function section."""
        num_funcs = _read_unsigned_int(f)
        functype_indices = [_read_unsigned_int(f) for _ in range(num_funcs)]
        print(
            f"Read function types (length {len(functype_indices)}): {functype_indices}"
        )
        return FunctionSection([Func(typeidx, [], []) for typeidx in functype_indices])


@dataclasses.dataclass
class TableSection(ModuleSection):
    """A table section."""

    tables: list[Table]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a table section."""
        num_tables = _read_unsigned_int(f)
        tables = [Table.read(f) for _ in range(num_tables)]
        print(f"Read tables: {tables}")
        return TableSection(tables)


@dataclasses.dataclass
class MemorySection(ModuleSection):
    """A memory section."""

    memories: list[Mem]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a memory section."""
        num_memories = _read_unsigned_int(f)
        memories = [Mem.read(f) for _ in range(num_memories)]
        print(f"Read memories: {memories}")
        return MemorySection(memories)


@dataclasses.dataclass
class GlobalSection(ModuleSection):
    """A global section."""

    global_vars: list[Global]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a global section."""
        num_globals = _read_unsigned_int(f)
        global_vars = [Global.read(f) for _ in range(num_globals)]
        print(f"Read globals: {global_vars}")
        return GlobalSection(global_vars)


@dataclasses.dataclass
class ExportSection(ModuleSection):
    """An export section."""

    exports: list[Export]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns an export section."""
        num_exports = _read_unsigned_int(f)
        exports = [Export.read(f) for _ in range(num_exports)]
        print(f"Read exports: {exports}")
        return ExportSection(exports)


@dataclasses.dataclass
class StartSection(ModuleSection):
    """A start section."""

    start_idx: int

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a start section."""
        start_idx = _read_unsigned_int(f)
        print(f"Read start: {start_idx}")
        return StartSection(start_idx)


@dataclasses.dataclass
class ElementSection(ModuleSection):
    """An element segment section."""

    elements: list[ElementSegment]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns an element section."""
        num_elements = _read_unsigned_int(f)
        elements = [ElementSegment.read(f) for _ in range(num_elements)]
        print(f"Read elements: {elements}")
        return ElementSection(elements)


@dataclasses.dataclass
class CodeSection(ModuleSection):
    """A code section."""

    code: list[Code]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a code section."""
        num_code = _read_unsigned_int(f)
        code = [Code.read(f) for _ in range(num_code)]
        print(f"Read code (len {len(code)})")
        return CodeSection(code)


@dataclasses.dataclass
class DataSection(ModuleSection):
    """A data section."""

    data: list[Data]

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a data section."""
        num_data = _read_unsigned_int(f)
        data = [Data.read(f) for _ in range(num_data)]
        print(f"Read data: {data}")
        return DataSection(data)


@dataclasses.dataclass
class DataCountSection(ModuleSection):
    """A data count section."""

    data_count: int

    @staticmethod
    def read(f: BytesIO) -> ModuleSection:
        """Reads and returns a data count section."""
        data_count = _read_unsigned_int(f)
        print(f"Read data count: {data_count}")
        return DataCountSection(data_count)


class Module:
    """Reads in a module.

    Based on https://webassembly.github.io/spec/core/binary/modules.html#binary-module.
    """

    sections: dict[Type[ModuleSection], ModuleSection]

    def __init__(self):
        # default sections
        self.sections = {
            TypeSection: TypeSection([]),
            ImportSection: ImportSection([]),
            FunctionSection: FunctionSection([]),
            TableSection: TableSection([]),
            MemorySection: MemorySection([]),
            GlobalSection: GlobalSection([]),
            ExportSection: ExportSection([]),
            StartSection: StartSection(0),
            ElementSection: ElementSection([]),
            CodeSection: CodeSection([]),
            DataSection: DataSection([]),
            DataCountSection: DataCountSection(0),
        }

    @staticmethod
    def from_file(f: str) -> Module:
        """Reads a module from a file."""
        with open(f, "rb") as data:
            return Module.read(data)

    @staticmethod
    def read(f: BinaryIO) -> Module:
        """Reads a module from a binary stream."""
        if f.read(4) != b"\x00\x61\x73\x6D":
            raise ValueError("Magic number (0061736D) not found.")
        version = f.read(4)
        if version != b"\x01\x00\x00\x00":
            raise ValueError(f"Unsupported version {binascii.hexlify(version)}.")

        module = Module()
        while True:
            try:
                section = Module.read_section(f)
                if isinstance(section, CustomSection):
                    continue
                module.sections[type(section)] = section
            except EOFError:
                break

        # Fixups

        # Replace import func type indices with actual FuncTypes.
        type_section: TypeSection = module.sections[TypeSection]
        import_section: ImportSection = module.sections[ImportSection]
        for import_ in import_section.imports:
            if isinstance(import_.desc, int):
                import_.desc = type_section.types[import_.desc]

        # Expand func section with code section
        func_section: FunctionSection = module.sections[FunctionSection]
        code_section: CodeSection = module.sections[CodeSection]
        assert len(func_section.funcs) == len(code_section.code)
        for i, func in enumerate(func_section.funcs):
            # "Unpack" the local var types.
            func.local_vars = []
            print(f"Fixup func {i}, local vars {code_section.code[i].local_vars}")
            for local in code_section.code[i].local_vars:
                func.local_vars.extend([local[1]] * local[0])
            print(f"  local_vars now {func.local_vars}")
            func.body = code_section.code[i].insns
        del module.sections[CodeSection]

        return module

    @staticmethod
    def read_section(f: BinaryIO) -> ModuleSection:
        """Reads a section.

        Returns:
          The section read.

        Raises:
          EOFError: upon reaching end of file.
        """
        section_types: list[Type[ModuleSection]] = [
            CustomSection,
            TypeSection,
            ImportSection,
            FunctionSection,
            TableSection,
            MemorySection,
            GlobalSection,
            ExportSection,
            StartSection,
            ElementSection,
            CodeSection,
            DataSection,
            DataCountSection,
        ]

        try:
            section_id = _read_byte(f)
        except IndexError as e:
            raise EOFError from e

        if section_id > len(section_types):
            raise ValueError(f"Unknown section ID {section_id}")

        section_len = _read_unsigned_int(f)
        print(f"Reading section {section_types[section_id]} length {section_len}")
        section_data = BytesIO(f.read(section_len))

        return section_types[section_id].read(section_data)
