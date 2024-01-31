using Derg.Wasm;

namespace Derg.Modules {
    public class LibC : IWasmAllocator {
        public void Free(Machine machine, Frame frame, Ptr buffer)
        {
            machine.CallExportedFunc<int>("free", frame, buffer.Addr);
        }

        public Ptr Malloc(Machine machine, Frame frame, int size)
        {
            return new Ptr(machine.CallExportedFunc<int, int>("malloc", frame, size));
        }

        public void Start(Machine machine, Frame frame) {
            machine.CallExportedFunc("_start", frame);
        }
    }
}
