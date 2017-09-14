from gym.envs.registration import register
from .ets2 import ETS2Env
from .ats import ATSEnv


register(
    id='ETS2-Indy500-v0',
    entry_point='autodrome.envs:ETS2Env',
    kwargs={'map': 'indy500'}
)

register(
    id='ATS-Indy500-v0',
    entry_point='autodrome.envs:ATSEnv',
    kwargs={'map': 'indy500'}
)
