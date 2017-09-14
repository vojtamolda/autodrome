#include <string>
#include <fstream>

#include <zmq.hpp>
#include <capnp/message.h>
#include <capnp/serialize.h>
#include "share/message.capnp.h"

#include <scssdk_telemetry.h>
#include <amtrucks/scssdk_ats.h>
#include <amtrucks/scssdk_telemetry_ats.h>
#include <eurotrucks2/scssdk_eut2.h>
#include <eurotrucks2/scssdk_telemetry_eut2.h>


using namespace std;
using namespace zmq;

class Telemetry {

public:
    Telemetry(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version);
    void config(const struct scs_telemetry_configuration_t *const config_info);
    void start();
    void frame_start(const struct scs_telemetry_frame_start_t *const frame_start_info);
    void frame_end();
    void pause();
    ~Telemetry();

    static SCSAPI_VOID channel_update(const scs_string_t channel, const scs_u32_t index, const scs_value_t *const value, const scs_context_t context);

    static SCSAPI_VOID config_callback(const scs_event_t event, const void *const event_info, scs_context_t const context);
    static SCSAPI_VOID start_callback(const scs_event_t event, const void *const event_info, scs_context_t const context);
    static SCSAPI_VOID frame_start_callback(const scs_event_t event, const void *const event_info, scs_context_t const context);
    static SCSAPI_VOID frame_end_callback(const scs_event_t event, const void *const event_info, scs_context_t const context);
    static SCSAPI_VOID pause_callback(const scs_event_t event, const void *const event_info, scs_context_t const context);

protected:
    class Helper {
    public:
        static void set(DPlacement::Builder builder, const scs_value_t *const value);
        static void set(FPlacement::Builder builder, const scs_value_t *const value);
        static void set(Euler::Builder builder, const scs_value_t *const value);
        static void set(DVector::Builder builder, const scs_value_t *const value);
        static void set(FVector::Builder builder, const scs_value_t *const value);
    };

    class capnp_socket_t: public socket_t {
    public:
        capnp_socket_t(context_t& context, int type, const Telemetry& telemetry);
        size_t send(capnp::MessageBuilder &message);
        unique_ptr<message_t> recv();
    private:
        const Telemetry& telemetry;
    };

    context_t zmq_context;
    capnp_socket_t data_socket;
    capnp::MallocMessageBuilder message_builder;

    bool paused;
    const scs_log_t print;

    void log(const string& message, const scs_log_type_t type=SCS_LOG_TYPE_message) const;
    bool check_steamid() const;
    bool check_version(const scs_telemetry_init_params_v100_t *const params, const scs_u32_t version) const;
    bool register_event(const scs_telemetry_init_params_v100_t *const params, const scs_event_t event, const scs_telemetry_event_callback_t callback);
    bool register_channel(const scs_telemetry_init_params_v100_t *const params, const scs_string_t channel, const scs_value_type_t type, const scs_context_t context);
};
