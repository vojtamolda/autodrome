#include <string>

#include <scssdk_telemetry.h>
#include <amtrucks/scssdk_ats.h>
#include <amtrucks/scssdk_telemetry_ats.h>
#include <eurotrucks2/scssdk_eut2.h>
#include <eurotrucks2/scssdk_telemetry_eut2.h>

using namespace std;


class Telemetry {

    public:
        Telemetry(const scs_telemetry_init_params_v100_t *const version_params);
        void configuration(const struct scs_telemetry_configuration_t *const configuration_info);
        void start();
        void frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info);
        void frame_end();
        void pause();
        ~Telemetry();

        void log(const scs_string_t message, const scs_log_type_t type=SCS_LOG_TYPE_message);
        static bool compatible_version(const scs_telemetry_init_params_v100_t *const params);

        static SCSAPI_VOID channel_update(const scs_string_t name, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context);

        static SCSAPI_VOID configuration_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
        static SCSAPI_VOID start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
        static SCSAPI_VOID frame_start_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
        static SCSAPI_VOID frame_end_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);
        static SCSAPI_VOID pause_callback(const scs_event_t event, const void *const event_info, const scs_context_t context);

    protected:
        bool paused;
        scs_log_t game_log;

        scs_value_dplacement_t world_placement;
        scs_value_dvector_t local_linear_velocity;
        scs_value_dvector_t local_angular_velocity;
        scs_value_double_t speed;

        scs_timestamp_t render_time;
        scs_timestamp_t simulation_time;
        scs_timestamp_t paused_simulation_time;

};
