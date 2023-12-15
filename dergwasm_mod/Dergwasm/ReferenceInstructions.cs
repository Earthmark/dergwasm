﻿namespace Derg
{
    public static class ReferenceInstructions
    {
        public static void RefNull(Instruction instruction, IMachine machine, Frame frame) =>
            machine.Push(new Value(0, 0));

        public static void RefIsNull(Instruction instruction, IMachine machine, Frame frame)
        {
            Value v = machine.Pop();
            machine.Push(new Value(v.IsNullRef()));
        }

        public static void Ref(Instruction instruction, IMachine machine, Frame frame)
        {
            int idx = instruction.Operands[0].Int;
            int addr = machine.GetFuncAddrFromIndex(idx);
            machine.Push(Value.RefOfFuncAddr(addr));
        }
    }
}
