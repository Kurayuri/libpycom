from collections.abc import Callable
import random
from typing import TypeAlias
from libpycom.SyntaxUtils import ListTupleUtils
import torch
import torch.nn.functional as F
import numpy as np
import math
from libpycom.calculation.math import mod
from transformers.cache_utils import DynamicCache
Tensor: TypeAlias = torch.Tensor | np.ndarray


class TensorUtils:
    @staticmethod
    def permute(tensor: Tensor, *dims):
        idxs = IndexUtils.completeSlice(tensor.ndim, *dims)
        return tensor.permute(*idxs)

    @staticmethod
    def getShape(tensor: Tensor | list | tuple, split=False):
        item = ListTupleUtils.getFirst(tensor)
        outer = ListTupleUtils.getShape(tensor)
        inner = item.shape
        return outer, inner if split else outer + inner

    @staticmethod
    def getNdim(tensor: Tensor | list | tuple):
        return len(TensorUtils.getShape(tensor))


class IndexUtils:
    '''stack   = (return,state,action)'''
    '''elem    = (feature,...)'''
    '''feature = (feature_value,...) | value'''
    @staticmethod
    def getStackedElemIndices(dim, stack_dim, elem_slice=None, stack_slice=None, reverse=False, flatten=False):
        if elem_slice is None or isinstance(elem_slice, int):
            elem_slice = slice(elem_slice, None)
        if stack_slice is None or isinstance(stack_slice, int):
            stack_slice = slice(stack_slice, None)

        n_stacks = math.ceil(dim / stack_dim)
        ans = [[] for _ in range(n_stacks)]

        if reverse:
            offset = mod(dim, stack_dim, reverse=True)
            for i in np.arange(n_stacks)[stack_slice]:
                ans[i] = np.arange(stack_dim * i + offset, stack_dim * (i + 1) + offset)[elem_slice].tolist()
            ans[0] = [i for i in ans[0] if i >= 0]
        else:
            for i in np.arange(n_stacks)[stack_slice]:
                ans[i] = np.arange(stack_dim * i, stack_dim * (i + 1))[elem_slice].tolist()
            ans[-1] = [i for i in ans[-1] if i < dim]
        if flatten:
            ans = [item for sublist in ans for item in sublist]
        return ans

    @staticmethod
    def completeSlice(ndim, *dims):
        assert dims.count(...), "At least one ellipsis is provided"
        if len(dims) == 0:
            dims = [...]

        def _convert_dim(dim):
            return ndim + dim if dim < 0 else dim

        _other = [i for i in range(ndim)]
        _prev = []
        _post = []

        at_prev = True
        for i in dims:
            if i is ...:
                at_prev = False
                continue
            i = _convert_dim(i)
            offset = ndim - len(_other)
            if at_prev:
                _prev.append(_other.pop(i - offset))
            else:
                _post.append(_other.pop(i - offset))
        return _prev + _other + _post


class CommonUtils:
    @staticmethod
    def sample(logits: np.ndarray | torch.Tensor, num_samples=1, preproc: Callable = F.softmax,
               method: str = "random.choices") -> tuple[Tensor, Tensor, Tensor]:

        _logits = torch.as_tensor(logits, dtype=torch.float32) if isinstance(logits, np.ndarray) else logits

        def _multinomial(probs: torch.Tensor):
            return torch.multinomial(probs.reshape(-1, probs.shape[-1]), num_samples=num_samples,
                                     replacement=True).reshape(*shape[:-1], num_samples)

        def _random(probs: torch.Tensor):
            probs_numpy = probs.cpu().numpy()
            samples = [random.choices(np.arange(shape[-1]), probs_numpy[idx], k=num_samples) for idx in np.ndindex(shape[:-1])]
            return torch.tensor(samples).reshape(*shape[:-1], num_samples).to(probs.device)

        shape = logits.shape

        probs = preproc(logits, dim=-1) if preproc is not None else logits

        if method == 'torch.multinomial':
            samples = _multinomial(probs)
        else:
            samples = _random(probs)

        sample_probs = probs.gather(-1, samples)
        sample_log_probs = torch.log(sample_probs)

        if isinstance(_logits, np.ndarray):
            samples = samples.cpu().numpy()
            sample_log_probs = sample_log_probs.cpu().numpy()
            probs = probs.cpu().numpy()

        return samples, sample_log_probs, probs

    @staticmethod
    def createExample(*dims):
        return torch.arange(np.prod(dims)).reshape(*dims)

class CacheUtils:
    @staticmethod
    def crop(cache: DynamicCache, max_length: int, reverse=False):
        """Crop the past key values up to a new `max_length` in terms of tokens. `max_length` can also be
        negative to remove `max_length` tokens. This is used in assisted decoding and contrastive search.
        transformers/cache_utils.py/DynamicCache.crop
        """
        # In case it is negative
        if max_length < 0:
            max_length = cache.get_seq_length() - abs(max_length)

        if cache.get_seq_length() <= max_length:
            return cache

        cache._seen_tokens = max_length
        for idx in range(len(cache.key_cache)):
            if cache.key_cache[idx] != []:
                if reverse:
                    cache.key_cache[idx] = cache.key_cache[idx][..., -max_length:, :]
                    cache.value_cache[idx] = cache.value_cache[idx][..., -max_length:, :]
                else:
                    cache.key_cache[idx] = cache.key_cache[idx][..., :max_length, :]
                    cache.value_cache[idx] = cache.value_cache[idx][..., :max_length, :]
        return cache
