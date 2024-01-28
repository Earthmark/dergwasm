﻿using Derg;
using Derg.Wasm;
using Elements.Core;
using Xunit;

namespace DergwasmTests
{
    public class ResoniteEnvSlotTests : TestMachine
    {
        FakeWorldServices worldServices;
        ResoniteEnv env;
        TestEmscriptenEnv emscriptenEnv;
        Frame frame;
        TestComponent testComponent;
        FakeSlot testSlot;
        FakeSlot rootSlot;

        public ResoniteEnvSlotTests()
        {
            ResonitePatches.Apply();

            worldServices = new FakeWorldServices();
            emscriptenEnv = new TestEmscriptenEnv();
            env = new ResoniteEnv(this, worldServices, emscriptenEnv);
            SimpleSerialization.Initialize(env);
            frame = emscriptenEnv.EmptyFrame(null);

            testComponent = new TestComponent(worldServices);
            testComponent.Initialize();

            rootSlot = worldServices.GetRootSlot() as FakeSlot;
            testSlot = new FakeSlot(worldServices, "name", rootSlot);
        }

        [Fact]
        public void RootSlotTest()
        {
            Assert.Equal((ulong)rootSlot.ReferenceID, env.slot__root_slot(frame));
        }

        [Fact]
        public void GetParentTest()
        {
            Assert.Equal(
                rootSlot.ReferenceID,
                env.slot__get_parent(frame, new WasmRefID<ISlot>(testSlot.ReferenceID))
            );
        }

        [Fact]
        public void GetParentFailsOnNonexistentRefID()
        {
            Assert.Equal(
                new RefID(0),
                env.slot__get_parent(frame, new WasmRefID<ISlot>(0xFFFFFFFFFFFFFFFFUL))
            );
        }

        [Fact]
        public void GetNameTest()
        {
            int dataPtr = env.slot__get_name(frame, (ulong)testSlot.ReferenceID);
            Assert.Equal(testSlot.Name, emscriptenEnv.GetUTF8StringFromMem(dataPtr));
        }

        [Fact]
        public void SetNameTest()
        {
            Buff<byte> buff = emscriptenEnv.AllocateUTF8StringInMem(frame, "new name");
            env.slot__set_name(frame, (ulong)testSlot.ReferenceID, buff.Ptr.Addr);
            Assert.Equal("new name", testSlot.Name);
        }
    }
}
