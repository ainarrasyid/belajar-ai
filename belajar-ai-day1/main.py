models = [
    { "nama": "Model 1", "ukuran_gb": 2.5, "cocok_untuk_m1": True },
    { "nama": "Model 2", "ukuran_gb": 3.0, "cocok_untuk_m1": False },
    { "nama": "Model 3", "ukuran_gb": 1.8, "cocok_untuk_m1": True },
]

def filter_model_mac(model_list):
    return [model["nama"] for model in model_list if model["cocok_untuk_m1"]]

print(filter_model_mac(models))