#include "telemetry.hpp"


static Telemetry* telemetry = NULL;

SCSAPI_RESULT scs_telemetry_init(const scs_u32_t version, const scs_telemetry_init_params_t *const init_params) {
    try {
        const scs_telemetry_init_params_v100_t *const params = static_cast<const scs_telemetry_init_params_v100_t *>(init_params);
        telemetry = new Telemetry(params, version);
        return SCS_RESULT_ok;
    } catch (exception& exc) {
        return SCS_RESULT_unsupported;
    }
}

SCSAPI_VOID scs_telemetry_shutdown(void) {
    delete telemetry;
    telemetry = NULL;
}
