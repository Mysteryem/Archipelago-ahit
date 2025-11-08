from worlds.LauncherComponents import launch, components, Component, Type


def launch_client(*args: str):
    from .client import run
    launch(run, name="FilterableTextClient", args=args)


components.append(Component("Filterable Text Client", func=launch_client, component_type=Type.CLIENT,
                            description="Connect to a multiworld using the text client (with toggleable filtering"
                                        " commands)."))
