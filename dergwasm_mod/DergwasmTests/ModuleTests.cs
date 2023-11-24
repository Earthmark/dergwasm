﻿using System.IO;
using System.Text;
using Derg;
using LEB128;
using Xunit;

namespace DergwasmTests
{
    public class ModuleTests
    {
        static void WriteString(BinaryWriter writer, string str)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(str);
            writer.WriteLEB128Unsigned((ulong)bytes.Length);
            writer.Write(bytes);
        }

        static void WriteTestFuncType(BinaryWriter writer)
        {
            writer.Write((byte)0x60); // FuncType tag
            writer.WriteLEB128Unsigned(2UL); // 2 args
            writer.Write((byte)ValueType.I32);
            writer.Write((byte)ValueType.I64);
            writer.WriteLEB128Unsigned(2UL); // 2 returns
            writer.Write((byte)ValueType.F32);
            writer.Write((byte)ValueType.F64);
        }

        static FuncType TestFuncType0 = new FuncType(
            new ValueType[] { ValueType.I64 },
            new ValueType[0]
        );
        static FuncType TestFuncType1 = new FuncType(
            new ValueType[] { ValueType.I32, ValueType.I64 },
            new ValueType[] { ValueType.F32, ValueType.F64 }
        );

        static void WriteTestTypeSection(BinaryWriter writer)
        {
            writer.Write((byte)1); // Type section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(2UL); // 2 FuncTypes

            sectionWriter.Write((byte)0x60); // FuncType tag
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 arg
            sectionWriter.Write((byte)ValueType.I64);
            sectionWriter.WriteLEB128Unsigned(0UL); // 0 returns

            sectionWriter.Write((byte)0x60); // FuncType tag
            sectionWriter.WriteLEB128Unsigned(2UL); // 2 args
            sectionWriter.Write((byte)ValueType.I32);
            sectionWriter.Write((byte)ValueType.I64);
            sectionWriter.WriteLEB128Unsigned(2UL); // 2 returns
            sectionWriter.Write((byte)ValueType.F32);
            sectionWriter.Write((byte)ValueType.F64);

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static TableType TestTableType0 = new TableType(new Limits(1), ValueType.FUNCREF);

        static void WriteTestTableType(BinaryWriter writer)
        {
            writer.Write((byte)ValueType.FUNCREF);
            writer.Write((byte)0); // No maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
        }

        static void WriteTestTableSection(BinaryWriter writer)
        {
            writer.Write((byte)4); // Table section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 table
            WriteTestTableType(sectionWriter);

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static Limits TestMemoryType0 = new Limits(1, 10);

        static void WriteTestMemoryType(BinaryWriter writer)
        {
            writer.Write((byte)1); // Has maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
            writer.WriteLEB128Unsigned(10UL); // Maximum 10
        }

        static void WriteTestMemorySection(BinaryWriter writer)
        {
            writer.Write((byte)5); // Memory section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 memory
            WriteTestMemoryType(sectionWriter);

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static GlobalType TestGlobalType0 = new GlobalType(ValueType.I32, true);

        static void WriteTestGlobalType(BinaryWriter writer)
        {
            writer.Write((byte)ValueType.I32);
            writer.Write((byte)1); // Mutable
        }

        static void WriteTestGlobalSection(BinaryWriter writer)
        {
            writer.Write((byte)6); // Global section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 global
            WriteTestGlobalType(sectionWriter);
            sectionWriter.Write((byte)InstructionType.NOP);
            sectionWriter.Write((byte)InstructionType.NOP);
            sectionWriter.Write((byte)InstructionType.END);

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static void WriteTestFunctionSection(BinaryWriter writer)
        {
            writer.Write((byte)3); // Function section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(4UL); // 4 functions
            sectionWriter.WriteLEB128Unsigned(0UL); // Type index 0
            sectionWriter.WriteLEB128Unsigned(0UL); // Type index 0
            sectionWriter.WriteLEB128Unsigned(1UL); // Type index 1
            sectionWriter.WriteLEB128Unsigned(1UL); // Type index 1

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static void WriteTestImportSection(BinaryWriter writer)
        {
            writer.Write((byte)2); // Import section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(5UL); // 5 imports

            WriteString(sectionWriter, "module1");
            WriteString(sectionWriter, "func1");
            sectionWriter.Write((byte)0); // Func import
            sectionWriter.WriteLEB128Unsigned(0UL); // Type index 0

            WriteString(sectionWriter, "module2");
            WriteString(sectionWriter, "func2");
            sectionWriter.Write((byte)0); // Func import
            sectionWriter.WriteLEB128Unsigned(1UL); // Type index 1

            WriteString(sectionWriter, "module3");
            WriteString(sectionWriter, "table1");
            sectionWriter.Write((byte)1); // Table import
            WriteTestTableType(sectionWriter);

            WriteString(sectionWriter, "module4");
            WriteString(sectionWriter, "memory1");
            sectionWriter.Write((byte)2); // Memory import
            WriteTestMemoryType(sectionWriter);

            WriteString(sectionWriter, "module5");
            WriteString(sectionWriter, "global1");
            sectionWriter.Write((byte)3); // Global import
            WriteTestGlobalType(sectionWriter);

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        static void WriteTestExportSection(BinaryWriter writer)
        {
            writer.Write((byte)7); // Export section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(4UL); // 4 exports

            WriteString(sectionWriter, "func1");
            sectionWriter.Write((byte)0); // Func export
            sectionWriter.WriteLEB128Unsigned(5UL); // Func index 5 (the last non-imported func)

            WriteString(sectionWriter, "table1");
            sectionWriter.Write((byte)1); // Table export
            sectionWriter.WriteLEB128Unsigned(1UL); // Table index 1 (the first non-imported table)

            WriteString(sectionWriter, "memory1");
            sectionWriter.Write((byte)2); // Memory export
            sectionWriter.WriteLEB128Unsigned(1UL); // Memory index 1 (the first non-imported memory)

            WriteString(sectionWriter, "global1");
            sectionWriter.Write((byte)3); // Global export
            sectionWriter.WriteLEB128Unsigned(1UL); // Global index 1 (the first non-imported global)

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
        }

        [Fact]
        public void ReadEmptyModuleWorks()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Empty(module.customData);
            Assert.Empty(module.FuncTypes);
            Assert.Empty(module.Imports);
            Assert.Empty(module.Exports);
            Assert.Empty(module.Funcs);
            Assert.Empty(module.Tables);
            Assert.Empty(module.Memories);
            Assert.Empty(module.Globals);
            Assert.Empty(module.ElementSegmentSpecs);
            Assert.Empty(module.DataSegments);
            Assert.Equal(-1, module.StartIdx);
            Assert.Equal(0, module.DataCount);
        }

        [Fact]
        public void ReadModuleTrapsOnBadMagic()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736101U);
            writer.Write(1U);
            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Assert.Throws<Trap>(() => Module.Read(reader));
        }

        [Fact]
        public void ReadModuleTrapsOnBadVersion()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(2U);
            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Assert.Throws<Trap>(() => Module.Read(reader));
        }

        [Fact]
        public void ReadsCustomSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            writer.Write((byte)0); // Custom section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            WriteString(sectionWriter, "custom section");
            sectionWriter.WriteLEB128Unsigned(4UL);
            sectionWriter.Write(0xF100FF1EU);
            sectionStream.Position = 0;

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());
            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Single(module.customData);
            Assert.Collection(module.customData, e => Assert.Equal("custom section", e.Name));
            Assert.Collection(
                module.customData,
                e => Assert.Equal(new byte[] { 0x1E, 0xFF, 0x00, 0xF1 }, e.Data)
            );
        }

        [Fact]
        public void ReadsFuncTypeCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            WriteTestFuncType(writer);
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            FuncType funcType = FuncType.Read(reader);

            Assert.Collection(
                funcType.args,
                e => Assert.Equal(ValueType.I32, e),
                e => Assert.Equal(ValueType.I64, e)
            );
            Assert.Collection(
                funcType.returns,
                e => Assert.Equal(ValueType.F32, e),
                e => Assert.Equal(ValueType.F64, e)
            );
        }

        [Fact]
        public void ReadFuncTypeTrapsOnBadTag()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)0x7F);
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            Assert.Throws<Trap>(() => FuncType.Read(reader));
        }

        [Fact]
        public void ReadsNoMaximumLimitsCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)0); // No maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            Limits limits = Limits.Read(reader);

            Assert.Equal(1U, limits.Minimum);
            Assert.False(limits.Maximum.HasValue);
        }

        [Fact]
        public void ReadsMaximumLimitsCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)1); // Has maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
            writer.WriteLEB128Unsigned(2UL); // Maximum 2
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            Limits limits = Limits.Read(reader);

            Assert.Equal(1U, limits.Minimum);
            Assert.True(limits.Maximum.HasValue);
            Assert.Equal(2U, limits.Maximum.Value);
        }

        [Fact]
        public void ReadLimitsTrapsOnBadFlag()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)2); // Bad flag
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            Assert.Throws<Trap>(() => Limits.Read(reader));
        }

        [Fact]
        public void ReadTableTypeCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)ValueType.FUNCREF);
            writer.Write((byte)0); // No maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            TableType tableType = TableType.Read(reader);

            Assert.Equal(ValueType.FUNCREF, tableType.ElementType);
            Assert.Equal(1U, tableType.Limits.Minimum);
            Assert.False(tableType.Limits.Maximum.HasValue);
        }

        [Fact]
        public void ReadTableTypeTrapsOnBadElementType()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)ValueType.I32); // Bad element type
            writer.Write((byte)0); // No maximum
            writer.WriteLEB128Unsigned(1UL); // Minimum 1
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            Assert.Throws<Trap>(() => TableType.Read(reader));
        }

        [Theory]
        [InlineData(0, false)]
        [InlineData(1, true)]
        public void ReadsGlobalTypeCorrectly(byte mutableFlag, bool expected)
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)ValueType.I32);
            writer.Write(mutableFlag);
            memStream.Position = 0;

            BinaryReader reader = new BinaryReader(memStream);

            GlobalType globalType = GlobalType.Read(reader);

            Assert.Equal(ValueType.I32, globalType.Type);
            Assert.Equal(expected, globalType.Mutable);
        }

        [Fact]
        public void ReadsElementSegmentTag0Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)0); // Tag 0

            // Offset expr
            writer.Write((byte)InstructionType.NOP);
            writer.Write((byte)InstructionType.END);

            writer.WriteLEB128Unsigned(2UL); // 2 element indexes
            writer.WriteLEB128Unsigned(100UL); // Element index 0
            writer.WriteLEB128Unsigned(101UL); // Element index 1

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<ActiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Equal(0, (elementSegmentSpec as ActiveElementSegmentSpec).TableIdx);
            Assert.Collection(
                (elementSegmentSpec as ActiveElementSegmentSpec).OffsetExpr,
                i => Assert.Equal(InstructionType.NOP, i.Type),
                i => Assert.Equal(InstructionType.END, i.Type)
            );
            Assert.Collection(
                elementSegmentSpec.ElemIndexes,
                i => Assert.Equal(100, i),
                i => Assert.Equal(101, i)
            );
            Assert.Null(elementSegmentSpec.ElemIndexExprs);
        }

        [Fact]
        public void ReadsElementSegmentTag1Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)1); // Tag 1

            writer.WriteLEB128Unsigned(0UL); // Elem type FUNCREF

            writer.WriteLEB128Unsigned(2UL); // 2 element indexes
            writer.WriteLEB128Unsigned(100UL); // Element index 0
            writer.WriteLEB128Unsigned(101UL); // Element index 1

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<PassiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Collection(
                elementSegmentSpec.ElemIndexes,
                i => Assert.Equal(100, i),
                i => Assert.Equal(101, i)
            );
            Assert.Null(elementSegmentSpec.ElemIndexExprs);
        }

        [Fact]
        public void ReadsElementSegmentTag2Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)2); // Tag 2

            writer.WriteLEB128Unsigned(100UL); // Table idx 100

            // Offset expr
            writer.Write((byte)InstructionType.NOP);
            writer.Write((byte)InstructionType.END);

            writer.WriteLEB128Unsigned(0UL); // Elem type FUNCREF

            writer.WriteLEB128Unsigned(2UL); // 2 element indexes
            writer.WriteLEB128Unsigned(100UL); // Element index 0
            writer.WriteLEB128Unsigned(101UL); // Element index 1

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<ActiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Equal(100, (elementSegmentSpec as ActiveElementSegmentSpec).TableIdx);
            Assert.Collection(
                (elementSegmentSpec as ActiveElementSegmentSpec).OffsetExpr,
                i => Assert.Equal(InstructionType.NOP, i.Type),
                i => Assert.Equal(InstructionType.END, i.Type)
            );
            Assert.Collection(
                elementSegmentSpec.ElemIndexes,
                i => Assert.Equal(100, i),
                i => Assert.Equal(101, i)
            );
            Assert.Null(elementSegmentSpec.ElemIndexExprs);
        }

        [Fact]
        public void ReadsElementSegmentTag3Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)3); // Tag 3

            writer.WriteLEB128Unsigned(0UL); // Elem type FUNCREF

            writer.WriteLEB128Unsigned(2UL); // 2 element indexes
            writer.WriteLEB128Unsigned(100UL); // Element index 0
            writer.WriteLEB128Unsigned(101UL); // Element index 1

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<DeclarativeElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Collection(
                elementSegmentSpec.ElemIndexes,
                i => Assert.Equal(100, i),
                i => Assert.Equal(101, i)
            );
            Assert.Null(elementSegmentSpec.ElemIndexExprs);
        }

        [Fact]
        public void ReadsElementSegmentTag4Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)4); // Tag 4

            // Offset expr
            writer.Write((byte)InstructionType.NOP);
            writer.Write((byte)InstructionType.END);

            writer.WriteLEB128Unsigned(2UL); // 2 element index exprs
            writer.Write((byte)InstructionType.END); // expr 0
            writer.Write((byte)InstructionType.NOP); // expr 1
            writer.Write((byte)InstructionType.END);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<ActiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Equal(0, (elementSegmentSpec as ActiveElementSegmentSpec).TableIdx);
            Assert.Collection(
                (elementSegmentSpec as ActiveElementSegmentSpec).OffsetExpr,
                i => Assert.Equal(InstructionType.NOP, i.Type),
                i => Assert.Equal(InstructionType.END, i.Type)
            );
            Assert.Null(elementSegmentSpec.ElemIndexes);
            Assert.Collection(
                elementSegmentSpec.ElemIndexExprs,
                e => Assert.Collection(e, i => Assert.Equal(InstructionType.END, i.Type)),
                e =>
                    Assert.Collection(
                        e,
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.END, i.Type)
                    )
            );
        }

        [Fact]
        public void ReadsElementSegmentTag5Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)5); // Tag 5

            writer.WriteLEB128Unsigned((int)ValueType.FUNCREF);

            writer.WriteLEB128Unsigned(2UL); // 2 element index exprs
            writer.Write((byte)InstructionType.END); // expr 0
            writer.Write((byte)InstructionType.NOP); // expr 1
            writer.Write((byte)InstructionType.END);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<PassiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Null(elementSegmentSpec.ElemIndexes);
            Assert.Collection(
                elementSegmentSpec.ElemIndexExprs,
                e => Assert.Collection(e, i => Assert.Equal(InstructionType.END, i.Type)),
                e =>
                    Assert.Collection(
                        e,
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.END, i.Type)
                    )
            );
        }

        [Fact]
        public void ReadsElementSegmentTag6Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)6); // Tag 6

            writer.WriteLEB128Unsigned(100UL); // Table idx 100

            // Offset expr
            writer.Write((byte)InstructionType.NOP);
            writer.Write((byte)InstructionType.END);

            writer.WriteLEB128Unsigned((int)ValueType.FUNCREF); // Elem type FUNCREF

            writer.WriteLEB128Unsigned(2UL); // 2 element index exprs
            writer.Write((byte)InstructionType.END); // expr 0
            writer.Write((byte)InstructionType.NOP); // expr 1
            writer.Write((byte)InstructionType.END);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<ActiveElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Equal(100, (elementSegmentSpec as ActiveElementSegmentSpec).TableIdx);
            Assert.Collection(
                (elementSegmentSpec as ActiveElementSegmentSpec).OffsetExpr,
                i => Assert.Equal(InstructionType.NOP, i.Type),
                i => Assert.Equal(InstructionType.END, i.Type)
            );
            Assert.Null(elementSegmentSpec.ElemIndexes);
            Assert.Collection(
                elementSegmentSpec.ElemIndexExprs,
                e => Assert.Collection(e, i => Assert.Equal(InstructionType.END, i.Type)),
                e =>
                    Assert.Collection(
                        e,
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.END, i.Type)
                    )
            );
        }

        [Fact]
        public void ReadsElementSegmentTag7Correctly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write((byte)7); // Tag 7

            writer.WriteLEB128Unsigned((int)ValueType.FUNCREF); // Elem type FUNCREF

            writer.WriteLEB128Unsigned(2UL); // 2 element index exprs
            writer.Write((byte)InstructionType.END); // expr 0
            writer.Write((byte)InstructionType.NOP); // expr 1
            writer.Write((byte)InstructionType.END);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            ElementSegmentSpec elementSegmentSpec = ElementSegmentSpec.Read(reader);

            Assert.IsType<DeclarativeElementSegmentSpec>(elementSegmentSpec);
            Assert.Equal(ValueType.FUNCREF, elementSegmentSpec.ElemType);
            Assert.Null(elementSegmentSpec.ElemIndexes);
            Assert.Collection(
                elementSegmentSpec.ElemIndexExprs,
                e => Assert.Collection(e, i => Assert.Equal(InstructionType.END, i.Type)),
                e =>
                    Assert.Collection(
                        e,
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.END, i.Type)
                    )
            );
        }

        [Fact]
        public void ReadsTypeSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);

            WriteTestTypeSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.FuncTypes,
                e =>
                    Assert.Equal(
                        new FuncType(new ValueType[] { ValueType.I64 }, new ValueType[0]),
                        e
                    ),
                e =>
                    Assert.Equal(
                        new FuncType(
                            new ValueType[] { ValueType.I32, ValueType.I64 },
                            new ValueType[] { ValueType.F32, ValueType.F64 }
                        ),
                        e
                    )
            );
        }

        [Fact]
        public void ReadsImportSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);

            WriteTestImportSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.Imports,
                e =>
                {
                    Assert.Equal("module1", e.ModuleName);
                    Assert.Equal("func1", e.Name);
                    Assert.IsType<FuncImport>(e);
                    Assert.Equal(TestFuncType0, (e as FuncImport).FuncType);
                },
                e =>
                {
                    Assert.Equal("module2", e.ModuleName);
                    Assert.Equal("func2", e.Name);
                    Assert.IsType<FuncImport>(e);
                    Assert.Equal(TestFuncType1, (e as FuncImport).FuncType);
                },
                e =>
                {
                    Assert.Equal("module3", e.ModuleName);
                    Assert.Equal("table1", e.Name);
                    Assert.IsType<TableImport>(e);
                    Assert.Equal(TestTableType0, (e as TableImport).TableType);
                },
                e =>
                {
                    Assert.Equal("module4", e.ModuleName);
                    Assert.Equal("memory1", e.Name);
                    Assert.IsType<MemoryImport>(e);
                    Assert.Equal(TestMemoryType0, (e as MemoryImport).MemoryLimits);
                },
                e =>
                {
                    Assert.Equal("module5", e.ModuleName);
                    Assert.Equal("global1", e.Name);
                    Assert.IsType<GlobalImport>(e);
                    Assert.Equal(TestGlobalType0, (e as GlobalImport).GlobalType);
                }
            );
        }

        [Fact]
        public void TestReadsFunctionSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);

            WriteTestFunctionSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.Funcs,
                e => Assert.Equal(TestFuncType0, e.Signature),
                e => Assert.Equal(TestFuncType0, e.Signature),
                e => Assert.Equal(TestFuncType1, e.Signature),
                e => Assert.Equal(TestFuncType1, e.Signature)
            );
        }

        [Fact]
        public void TestReadsTableSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);

            WriteTestTableSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(module.Tables, e => Assert.Equal(TestTableType0, e));
        }

        [Fact]
        public void TestReadsMemorySectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);

            WriteTestMemorySection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(module.Memories, e => Assert.Equal(TestMemoryType0, e));
        }

        [Fact]
        public void TestReadsGlobalSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);

            WriteTestGlobalSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.Globals,
                e =>
                {
                    Assert.Equal(TestGlobalType0, e.Type);
                    Assert.Collection(
                        e.InitExpr,
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.NOP, i.Type),
                        i => Assert.Equal(InstructionType.END, i.Type)
                    );
                }
            );
        }

        [Fact]
        public void TestReadsExportSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U);
            writer.Write(1U);
            WriteTestTypeSection(writer);
            WriteTestImportSection(writer);
            WriteTestFunctionSection(writer);
            WriteTestTableSection(writer);
            WriteTestMemorySection(writer);
            WriteTestGlobalSection(writer);

            WriteTestExportSection(writer);

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.Exports,
                e =>
                {
                    Assert.Equal("func1", e.Name);
                    Assert.IsType<FuncExport>(e);
                    Assert.Equal(5, (e as FuncExport).Idx);
                },
                e =>
                {
                    Assert.Equal("table1", e.Name);
                    Assert.IsType<TableExport>(e);
                    Assert.Equal(1, (e as TableExport).Idx);
                },
                e =>
                {
                    Assert.Equal("memory1", e.Name);
                    Assert.IsType<MemoryExport>(e);
                    Assert.Equal(1, (e as MemoryExport).Idx);
                },
                e =>
                {
                    Assert.Equal("global1", e.Name);
                    Assert.IsType<GlobalExport>(e);
                    Assert.Equal(1, (e as GlobalExport).Idx);
                }
            );
        }

        [Fact]
        public void TestReadsStartSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U); // Magic
            writer.Write(1U); // Version

            writer.Write((byte)8); // Start section

            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(100UL); // Start function index 100

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Equal(100, module.StartIdx);
        }

        [Fact]
        public void TestReadsElementSegmentSectionCorrectly()
        {
            MemoryStream memStream = new MemoryStream();
            BinaryWriter writer = new BinaryWriter(memStream);
            writer.Write(0x6D736100U); // Magic
            writer.Write(1U); // Version

            WriteTestTypeSection(writer);
            WriteTestFunctionSection(writer);
            WriteTestTableSection(writer);

            writer.Write((byte)9); // Element segment section
            MemoryStream sectionStream = new MemoryStream();
            BinaryWriter sectionWriter = new BinaryWriter(sectionStream);
            sectionWriter.WriteLEB128Unsigned(2UL); // 2 element segments

            // First element segment
            sectionWriter.Write((byte)0); // Tag 0
            sectionWriter.Write((byte)InstructionType.END);
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 element index
            sectionWriter.WriteLEB128Unsigned(100UL); // Elem index 100

            // Second element segment
            sectionWriter.Write((byte)1); // Tag 1
            sectionWriter.WriteLEB128Unsigned(0UL); // FUNCREF
            sectionWriter.WriteLEB128Unsigned(1UL); // 1 element index
            sectionWriter.WriteLEB128Unsigned(101UL); // Elem index 101

            writer.WriteLEB128Unsigned((ulong)sectionStream.Length);
            writer.Write(sectionStream.ToArray());

            memStream.Position = 0;
            BinaryReader reader = new BinaryReader(memStream);

            Module module = Module.Read(reader);

            Assert.Collection(
                module.ElementSegmentSpecs,
                e => Assert.IsType<ActiveElementSegmentSpec>(e),
                e => Assert.IsType<PassiveElementSegmentSpec>(e)
            );
        }
    }
}
