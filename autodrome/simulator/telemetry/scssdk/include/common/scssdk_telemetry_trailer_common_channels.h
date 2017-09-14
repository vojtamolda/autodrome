/**
 * @file scssdk_telemetry_trailer_common_channels.h
 *
 * @brief Trailer telemetry specific constants for channels.
 *
 * See scssdk_telemetry_truck_common_channels.h for more info.
 */
#ifndef SCSSDK_TELEMETRY_TRAILER_COMMON_CHANNELS_H
#define SCSSDK_TELEMETRY_TRAILER_COMMON_CHANNELS_H

#include "../scssdk.h"

SCSSDK_HEADER

/**
 * @brief Is the trailer connected to the truck?
 *
 * Type: bool
 */
#define SCS_TELEMETRY_TRAILER_CHANNEL_connected                         "trailer.connected"

/**
 * @name Channels similar to the truck ones
 *
 * See scssdk_telemetry_truck_common_channels.h for description of
 * corresponding truck channels
 */
//@{
#define SCS_TELEMETRY_TRAILER_CHANNEL_world_placement                   "trailer.world.placement"
#define SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity             "trailer.velocity.linear"
#define SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity            "trailer.velocity.angular"
#define SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration         "trailer.acceleration.linear"
#define SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration        "trailer.acceleration.angular"

// Damage.

#define SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis                      "trailer.wear.chassis"

// Wheels.

#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection             "trailer.wheel.suspension.deflection"
#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground                   "trailer.wheel.on_ground"
#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance                   "trailer.wheel.substance"
#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity                    "trailer.wheel.angular_velocity"
#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering                    "trailer.wheel.steering"
#define SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation                    "trailer.wheel.rotation"
//@}

SCSSDK_FOOTER

#endif // SCSSDK_TELEMETRY_TRAILER_COMMON_CHANNELS_H

/* eof */
