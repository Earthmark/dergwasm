﻿using Derg;
using Derg.Wasm;
using FrooxEngine;
using Xunit;

namespace DergwasmTests
{
    public class ResoniteEnvValueGetSetTests : TestMachine
    {
        FakeWorldServices worldServices;
        ResoniteEnv env;
        TestEmscriptenEnv emscriptenEnv;
        Frame frame;
        TestComponent testComponent;

        public ResoniteEnvValueGetSetTests()
        {
            ResonitePatches.Apply();
            worldServices = new FakeWorldServices();
            emscriptenEnv = new TestEmscriptenEnv();
            env = new ResoniteEnv(this, worldServices, emscriptenEnv);
            SimpleSerialization.Initialize(env);
            frame = emscriptenEnv.EmptyFrame(null);

            testComponent = new TestComponent(worldServices);
            testComponent.Initialize();
        }

        [Fact]
        public void GetValueUnsetIntIsDefaultedTest()
        {
            var dataPtr = new Ptr<int>(4);


            Assert.Equal(
                ResoniteError.Success,
                env.value__get(frame, testComponent.IntField.GetWasmRef<IValue<int>>(), dataPtr)
            );
            Assert.Equal(0, HeapGet(dataPtr));
        }

        [Fact]
        public void GetValueIntTest()
        {
            testComponent.IntField.Value = 1;
            var dataPtr = new Ptr<int>(4);

            Assert.Equal(
                ResoniteError.Success,
                env.value__get(frame, testComponent.IntField.GetWasmRef<IValue<int>>(), dataPtr)
            );
            Assert.Equal(1, HeapGet(dataPtr));
        }

        [Fact]
        public void GetValueFailsOnNonexistentRefID()
        {
            Assert.Equal(ResoniteError.InvalidRefId, env.value__get(frame, new WasmRefID<IValue<int>>(0xFFFFFFFFFFFFFFFFUL), new Ptr<int>(4)));
        }

        [Fact]
        public void GetValueFailsOnWrongType()
        {
            Assert.Equal(
                ResoniteError.InvalidRefId,
                env.value__get(frame, new WasmRefID<IValue<double>>(testComponent.IntField.ReferenceID), new Ptr<double>(4))
            );
        }

        [Fact]
        public void GetValueFailsOnNullDataPtr()
        {
            Assert.Equal(
                ResoniteError.NullArgument,
                env.value__get(frame, testComponent.IntField.GetWasmRef<IValue<int>>(), Ptr<int>.Null)
            );
        }

        [Fact]
        public void GetValueFloatTest()
        {
            testComponent.FloatField.Value = 1;
            var dataPtr = new Ptr<float>(4);

            Assert.Equal(
                ResoniteError.Success,
                env.value__get(frame, testComponent.FloatField.GetWasmRef<IValue<float>>(), dataPtr)
            );
            Assert.Equal(1, HeapGet(dataPtr));
        }

        [Fact]
        public void GetValueDoubleTest()
        {
            testComponent.DoubleField.Value = 1;
            var dataPtr = new Ptr<double>(4);

            Assert.Equal(
                ResoniteError.Success,
                env.value__get(frame, testComponent.DoubleField.GetWasmRef<IValue<double>>(), dataPtr)
            );
            Assert.Equal(1, HeapGet(dataPtr));
        }

        [Fact]
        public void SetValueTest()
        {
            var dataPtr = new Ptr<int>(4);
            HeapSet(dataPtr, 12);
            Assert.Equal(
                ResoniteError.Success,
                env.value__set(frame, testComponent.IntField.GetWasmRef<IValue<int>>(), dataPtr)
            );
            Assert.Equal(12, testComponent.IntField.Value);
        }

        [Fact]
        public void SetValueFailsOnNonexistentRefID()
        {
            var dataPtr = new Ptr<int>(4);
            Assert.Equal(ResoniteError.InvalidRefId, env.value__set(frame, new WasmRefID<IValue<int>>(0xFFFFFFFFFFFFFFFFUL), dataPtr));
        }

        [Fact]
        public void SetValueFailsOnWrongType()
        {
            var dataPtr = new Ptr<double>(4);
            Assert.Equal(
                ResoniteError.InvalidRefId,
                env.value__set(frame, new WasmRefID<IValue<double>>(testComponent.IntField.ReferenceID), dataPtr)
            );
        }

        [Fact]
        public void SetValueFailsOnNullDataPtr()
        {
            Assert.Equal(
                ResoniteError.NullArgument,
                env.value__set(frame, testComponent.IntField.GetWasmRef<IValue<int>>(), default)
            );
        }
    }
}
