﻿using Elements.Core;
using System;

namespace Derg
{
    // The interface to a WASM machine.
    public interface IMachine
    {
        // Gets the value at the top of the current frame's label stack.
        Value TopOfStack { get; }

        // The current frame. Getting peeks at the current frame while setting will push a frame.
        Frame Frame { get; set; }

        // The label at the top of the current frame's label stack. Getting peeks at the current label,
        // while setting will push a label.
        Label Label { get; set; }

        // Whether there is at least one label on the current frame's label stack.
        bool HasLabel();

        // The current program counter from the current frame.
        int PC { get; set; }

        // Pushes the given value onto the stack.
        void Push(Value val);

        void Push(bool val);
        void Push(int val);
        void Push(uint val);
        void Push(long val);
        void Push(ulong val);
        void Push(float val);
        void Push(double val);

        // Pops the top value off the stack.
        Value Pop();

        unsafe T Pop<T>()
            where T : unmanaged;

        // Gets the locals for the current frame.
        Value[] Locals { get; }

        // Adds the given global to the machine, returning its address.
        int AddGlobal(Value global);

        // Gets the global address for the current module's index.
        int GetGlobalAddrForIndex(int idx);

        // Gets the machine's globals.
        Value[] Globals { get; }

        // Gets the number of values on the stack.
        int StackLevel();

        // Remove stack values from the given level (where the bottom of the stack is 0)
        // to the top of the stack minus the arity. Thus, after this operation, there
        // will be from_level + arity values on the stack.
        void RemoveStack(int from_level, int arity);

        // Pop a frame. This effectively returns from the current function.
        void PopFrame();

        // Pops a label off the current frame.
        Label PopLabel();

        // Gets the FuncType for the given index, using the current frame's module
        // to map the index to the machine's type address.
        FuncType GetFuncTypeFromIndex(int idx);

        // Adds the given table to the machine, returning its address.
        int AddTable(Table table);

        // Gets the Table for the given address.
        Table GetTable(int addr);

        // Gets the Table for the given index, using the current frame's module
        // to map the index to the machine's table address.
        Table GetTableFromIndex(int idx);

        // Adds the given element segment to the machine, returning its address.
        int AddElementSegment(ElementSegment elementSegment);

        // Gets the ElementSegment for the given index, using the current frame's module
        // to map the index to the machine's element segment address.
        ElementSegment GetElementSegmentFromIndex(int idx);

        // Nulls out the ElementSegment for the given index, using the current frame's module
        // to map the index to the machine's element segment address.
        void DropElementSegmentFromIndex(int idx);

        // Adds the given memory to the machine, returning its address.
        int AddMemory(Memory memory);

        // Gets the Memory for the given address.
        Memory GetMemory(int addr);

        // Gets the Memory for the given index, using the current frame's module
        // to map the index to the machine's memory address.
        Memory GetMemoryFromIndex(int idx);

        // A shortcut to get to the data in Memory 0.
        byte[] Memory0 { get; }

        // Gets a span of bytes from Memory 0.
        Span<byte> Span0(int offset, int sz);

        // Adds the given data segment to the machine, returning its address.
        int AddDataSegment(byte[] data);

        // Gets the DataSegment for the given index, using the current frame's module
        // to map the index to the machine's data segment address.
        byte[] GetDataSegmentFromIndex(int idx);

        // Gets the address of the data segment for the given index, using the current frame's module
        // to map the index to the machine's data segment address.
        int GetDataSegmentAddrFromIndex(int idx);

        // Nulls out the DataSegment for the given index, using the current frame's module
        // to map the index to the machine's data segment address.
        void DropDataSegmentFromIndex(int idx);

        // Adds the given function to the machine, returning its address.
        int AddFunc(Func func);

        // Gets the function at the given address.
        Func GetFunc(int addr);

        // Gets the function address for the given index, using the current frame's module
        // to map the index to the machine's function address.
        int GetFuncAddrFromIndex(int idx);

        // Invokes the function at the given index, using the current frame's module
        // to map the index to the machine's function address. Note that you can only
        // invoke a function in the current module or on the host using this. If you
        // need to invoke a function outside the module, use InvokeExternalFunc().
        void InvokeFuncFromIndex(int idx);

        void InvokeFunc(int addr);

        void Step(int n = 1);
    }
}
