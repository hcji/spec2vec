from copy import deepcopy
from gensim.models import Word2Vec
import json
import numpy as np
import os
import scipy.sparse
from typing import Union


def export_model(model: Word2Vec,
                 output_model_file: Union[str, os.PathLike],
                 output_weights_file: Union[str, os.PathLike]):
    """
    Write a lightweight version of a :class:`~gensim.model.Word2Vec` model to disk. Such a model can be read to
    calculate scores but is not capable of further training.

    Parameters
    ----------
    model:
        :class:`~gensim.models.Word2Vec` trained model.
    output_model_file:
        A path of json file to save the model.
    output_weights_file:
        A path of `.npy` file to save the model's weights.
    """
    model = deepcopy(model)
    keyedvectors = extract_keyedvectors(model)
    weights = keyedvectors.pop("vectors", KeyError("The model contains no weights."))
    keyedvectors["__weights_format"] = get_weights_format(weights)

    save_model(keyedvectors, output_model_file)
    save_weights(keyedvectors, weights, output_weights_file)


def save_weights(keyedvectors: dict,
                 weights: Union[np.ndarray, scipy.sparse.csr_matrix, scipy.sparse.csc_matrix],
                 output_weights_file: Union[str, os.PathLike]):
    """
    Write model's weights to disk in `.npy` dense array format. If the weights are sparse, they are converted to dense
    prior to saving.
    """
    if not (keyedvectors["__numpys"] or keyedvectors["__scipys"] or keyedvectors["__ignoreds"]):
        raise AttributeError("The model contains no weights.")
    elif keyedvectors["__scipys"]:
        weights = weights.toarray()

    np.save(output_weights_file, weights, allow_pickle=False)


def save_model(keyedvectors: dict, output_model_file: Union[str, os.PathLike]):
    """Write model's metadata to disk in json format."""
    with open(output_model_file, "w") as f:
        json.dump(keyedvectors, f)


def get_weights_format(weights: Union[np.ndarray, scipy.sparse.csr_matrix, scipy.sparse.csc_matrix]) -> str:
    """
    Get the array format of the model's weights.

    Parameters
    ----------
    weights:
        Model's weights.

    Returns
    -------
    weights_format:
        Format of the model's weights.
    """
    if isinstance(weights, np.ndarray):
        return "np.ndarray"
    elif isinstance(weights, scipy.sparse.csr_matrix):
        return "csr_matrix"
    elif isinstance(weights, scipy.sparse.csc_matrix):
        return "csc_matrix"
    else:
        raise NotImplementedError("The model's weights format is not supported.")


def extract_keyedvectors(model: Word2Vec) -> dict:
    """
    Extract :class:`~gensim.models.KeyedVectors` object from the model, convert it to a dictionary and
    remove redundant keys.

    Parameters
    ----------
    model:
        :class:`~gensim.models.Word2Vec` trained model.

    Returns
    -------
    keyedvectors:
        Dictionary representation of :class:`~gensim.models.KeyedVectors` without redundant keys.
    """
    keyedvectors = model.wv.__dict__
    keyedvectors.pop("vectors_lockf", None)
    keyedvectors.pop("expandos", None)
    return keyedvectors
