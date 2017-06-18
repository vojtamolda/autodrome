@0xec842aaa492eb782;

# scs_float_t
using Float = Float32;

# scs_double_t
using Double = Float64;

# scs_timestamp_t
using Timestamp = UInt64;

# scs_float2_t
struct Float2 {
  x @0 :Float;
  y @1 :Float;
}

# scs_float3_t
struct Float3 {
  x @0 :Float;
  y @1 :Float;
  z @2 :Float;
}

# scs_float4_t
struct Float4 {
  w @0 :Float;
  x @1 :Float;
  y @2 :Float;
  z @3 :Float;
}

# scs_quaternion_t
struct Quaternion {
  w @0 :Float;
  x @1 :Float;
  y @2 :Float;
  z @3 :Float;
}

# scs_fvector_t
struct FVector {
  x @0 :Float;
  y @1 :Float;
  z @2 :Float;
}

# scs_dvector_t
struct DVector {
  x @0 :Double;
  y @1 :Double;
  z @2 :Double;
}

# scs_euler_t
struct Euler {
  heading @0 :Float;
  pitch @1 :Float;
  roll @2 :Float;
}

# scs_fplacement_t
struct FPlacement {
  position @0 :FVector;
  orientation @1 :Euler;
}

# scs_dplacement_t
struct DPlacement {
  position @0 :DVector;
  orientation @1 :Euler;
}
