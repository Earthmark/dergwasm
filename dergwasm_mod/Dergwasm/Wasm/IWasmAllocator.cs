namespace Derg.Wasm
{
    public interface IWasmAllocator
    {
        Ptr Malloc(Machine machine, Frame frame, int size);
        void Free(Machine machine, Frame frame, Ptr buffer);
    }
}
