import math

def erlang_c(traffic_intensity, agents):
    """
    Erlang C calculation.
    traffic_intensity = lambda * AHT
    agents = number of staffed agents
    """
    if agents <= traffic_intensity:
        return 1.0  # system is overloaded

    sum_terms = sum((traffic_intensity ** n) / math.factorial(n) for n in range(agents))
    p0 = sum_terms + (traffic_intensity ** agents) / (math.factorial(agents) * (1 - (traffic_intensity / agents)))

    erlang_c = ((traffic_intensity ** agents) / (math.factorial(agents) * (1 - (traffic_intensity / agents)))) / p0
    return erlang_c


def required_agents(volume, aht, sl=0.8, asa=20):
    """
    Estimate required agents using Erlang C.
    volume = contacts
    aht = average handling time in seconds
    sl = service level target
    asa = target speed of answer
    """
    traffic_intensity = (volume * aht) / 3600  # traffic in erlangs

    for agents in range(1, 300):
        e_c = erlang_c(traffic_intensity, agents)
        asa_calc = (e_c * aht) / (agents * (1 - (traffic_intensity / agents)))

        service_level = 1 - (e_c * math.exp(-(agents - traffic_intensity) * (asa / aht)))

        if service_level >= sl:
            return agents

    return 300  # fallback
