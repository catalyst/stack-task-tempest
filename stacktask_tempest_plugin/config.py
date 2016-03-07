from oslo_config import cfg

service_available_group = cfg.OptGroup(
    name="service_available",
    title="Available OpenStack Services"
)

ServiceAvailableGroup = [
    cfg.BoolOpt("stacktask", default=False,
                help="Whether or not Stacktask is expected to be available")
]

stacktask_group = cfg.OptGroup(
    name="stacktask",
    title="Hello World Test Variables"
)

StacktaskGroup = [
    cfg.StrOpt("my_custom_variable", default="custom value",
               help="My custom variable.")
]
