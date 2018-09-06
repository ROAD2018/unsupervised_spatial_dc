"""!
@brief A dataset creation which is compatible with pytorch framework

@author Efthymios Tzinis {etzinis2@illinois.edu}
@copyright University of illinois at Urbana Champaign
"""

import os
import sys
import numpy as np
from random import shuffle
from pprint import pprint
from torch.utils.data import Dataset, DataLoader

root_dir = os.path.join(
           os.path.dirname(os.path.realpath(__file__)),
           '../../')
sys.path.insert(0, root_dir)

import spatial_two_mics.data_loaders.timit as timit_loader


class PytorchCompatibleDataset(Dataset):
    """
    This is a general compatible class for pytorch datasets all other
    subclasses should inherit from this one and implement a sampler
    in order to create the appropriate combinations of mixtures
    """
    def __init__(self,
                 audio_dataset_name="timit"):
        if audio_dataset_name.lower() == "timit":
            self.data_loader = timit_loader.TimitLoader()
        else:
            raise NotImplementedError("Dataset Loader: {} is not yet "
                  "implemented.".format(audio_dataset_name))


class RandomCombinations(PytorchCompatibleDataset):
    def __init__(self,
                 audio_dataset_name="timit",
                 n_mixtures=0,
                 n_mixed_sources=2,
                 genders_mixtures=None,
                 excluded_speakers=None,
                 subset_of_speakers='train'):
        super(RandomCombinations,
              self).__init__(audio_dataset_name=audio_dataset_name)

        data_dic = self.data_loader.load()
        if excluded_speakers is None:
            excluded_speakers = []

        self.genders_mixtures = genders_mixtures
        valid_genders = [(g in ['f', 'm'])
                         for g in self.genders_mixtures]
        assert valid_genders, ('Valid genders for mixtures are f and m')

        self.used_speakers = self.get_available_speakers(
                                  data_dic,
                                  subset_of_speakers,
                                  excluded_speakers)

        mixture_combinations = self.get_mixture_combinations(
                                    data_dic[subset_of_speakers],
                                    n_mixed_sources=n_mixed_sources,
                                    n_mixtures=n_mixtures)

    def get_available_speakers(self,
                               data_dic,
                               subset_of_speakers,
                               excluded_speakers):
        try:
            available_speakers = sorted(list(data_dic[
                                 subset_of_speakers].keys()))
        except KeyError:
            print("Subset: {} not available".format(subset_of_speakers))
            raise KeyError

        valid_speakers = []
        for speaker in available_speakers:

            if ((speaker not in excluded_speakers) and
                (data_dic[subset_of_speakers][speaker]['gender'] in
                 self.genders_mixtures)):
                valid_speakers.append(speaker)

        return valid_speakers

    @staticmethod
    def random_combinations(iterable, r):
        iter_len = len(iterable)
        max_combs = 1
        for i in np.arange(r):
            max_combs *= (iter_len - i + 1) / (i+1)

        already_seen = set()
        c = 0
        while c < max_combs:
            indexes = sorted(np.random.choice(iter_len, r))
            str_indexes = str(indexes)
            if str_indexes in already_seen:
                continue
            else:
                already_seen.add(str_indexes)

            c += 1
            yield [iterable[i] for i in indexes]

    def acquire_mixture_information(self,
                                    speaker_dic,
                                    combination_info):
        return None

    def get_only_valid_mixture_combinations(self,
                                            possible_sources,
                                            speakers_dic,
                                            n_mixed_sources=2,
                                            n_mixtures=0):
        mixtures_generator = self.random_combinations(possible_sources,
                                                      n_mixed_sources)

        if n_mixtures <= 0:
            print("All available mixtures that can be generated would "
                  " be: {}!".format(len(list(mixtures_generator))))
            print("Please Select a number of mixtures > 0")

        valid_mixtures = []

        while len(valid_mixtures) < n_mixtures:
            possible_comb = next(mixtures_generator)
            genders_in_mix = [x['gender'] for x in possible_comb]
            good_gender_mix = [g in genders_in_mix
                               for g in self.genders_mixtures]
            if not all(good_gender_mix):
                # not a valid gender
                continue

            valid_mixtures.append(self.acquire_mixture_information(
                                       speakers_dic,
                                       possible_comb))

        return valid_mixtures

    def get_mixture_combinations(self,
                                 speakers_dic,
                                 n_mixed_sources=2,
                                 n_mixtures=0):
        possible_sources = []
        for speaker in self.used_speakers:
            sentences = list(speakers_dic[speaker]['sentences'].keys())
            gender = speakers_dic[speaker]['gender']
            possible_sources += [{'speaker_id': speaker,
                                  'gender': gender,
                                  'sentence_id': sentence}
                                 for sentence in sentences]

        shuffle(possible_sources)

        valid_combinations = self.get_only_valid_mixture_combinations(
                                  possible_sources,
                                  speakers_dic,
                                  n_mixed_sources=n_mixed_sources,
                                  n_mixtures=n_mixtures)



        mixtures = []

        input()
        return mixtures


if __name__ == "__main__":
    timit_random_combs = RandomCombinations(
                         audio_dataset_name="timit",
                         genders_mixtures=['m', 'f'],
                         subset_of_speakers='test',
                         n_mixtures=10,
                         n_mixed_sources=4,
                         excluded_speakers=['mwew0'])

