"""
 Copyright 2022 Johns Hopkins University  (Author: Jesus Villalba)
 Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)
"""

from pathlib import Path
from typing import Dict, Optional, Union

import yaml

from .class_info import ClassInfo
from .feature_set import FeatureSet
from .misc import PathLike
from .recording_set import RecordingSet
from .segment_set import SegmentSet
from .enrollment_map import EnrollmentMap
from .trial_key import TrialKey
from .trial_ndx import TrialNdx
from .sparse_trial_key import SparseTrialKey


class Dataset:
    """ Class that contains all objects 
        (segments, recordings, features, class_infos) that 
        conform a dataset

        Attributes:
          segments:     SegmentSet object or path to it. 
          classes:      Dictionary of ClassInfo objects or paths to then 
          recordings:   Dictionary of RecordingSet objects or paths to then 
          features:     Dictionary of FeatureSet objects or paths to then 
          enrollments:  Dictionary of EnrollmentMap objects or paths to then 
          trials:       Dictionary of TrialKey/TrialNdx/SparseTrialKey objects 
            or paths to then 
          sparse_trials: load trial keys using the SparseTrialKey class instead 
              of TrialKey class.
          table_sep:    Column separator when reading/writting tables

    """

    def __init__(
        self,
        segments: Union[SegmentSet, PathLike],
        classes: Optional[Dict[str, Union[ClassInfo, PathLike]]] = None,
        recordings: Optional[Dict[str, Union[RecordingSet, PathLike]]] = None,
        features: Optional[Dict[str, Union[FeatureSet, PathLike]]] = None,
        enrollments: Optional[Dict[str, Union[EnrollmentMap, PathLike]]] = None,
        trials: Optional[
            Dict[str, Union[TrialKey, TrialNdx, SparseTrialKey, PathLike]]
        ] = None,
        sparse_trials: bool = False,
        table_sep: Optional[str] = None,
    ):

        if isinstance(segments, SegmentSet):
            self._segments = segments
            self._segments_path = None
        else:
            assert isinstance(segments, (str, Path))
            self._segments = None
            self._segments_path = Path(segments)

        self._classes, self._classes_paths = self._parse_dict_args(classes, ClassInfo)

        self._recordings, self._recordings_paths = self._parse_dict_args(
            recordings, RecordingSet
        )

        self._features, self._features_paths = self._parse_dict_args(
            features, FeatureSet
        )
        self._enrollments, self._enrollments_paths = self._parse_dict_args(
            enrollments, EnrollmentMap,
        )
        self._trials, self._trials_paths = self._parse_dict_args(
            trials, (TrialKey, TrialNdx, SparseTrialKey),
        )

        self.sparse_trials = sparse_trials
        self.table_sep = table_sep

    def _parse_dict_args(self, data, types):
        if data is None:
            return None, None

        assert isinstance(data, dict)
        objects = {k: (v if isinstance(v, types) else None) for k, v in data.items()}
        paths = {
            k: (v if isinstance(v, (str, Path)) else None) for k, v in data.items()
        }

        return objects, paths

    def segments(self, keep_loaded: bool = True):
        if self._segments is None:
            assert self._segments_path is not None
            segments = SegmentSet.load(self.segments_path, sep=self.table_sep)
            if keep_loaded:
                self._segments = segments
            return segments

        return self._segments

    def recordings_value(self, key: str, keep_loaded: bool = True):
        if self._recordings[key] is None:
            assert self._recordings_paths[key] is not None
            recordings = RecordingSet.load(
                self._recordings_paths[key], sep=self.table_sep
            )
            if keep_loaded:
                self._recordings[key] = recordings

        return self._recordings[key]

    def features_value(self, key: str, keep_loaded: bool = True):
        if self._features[key] is None:
            assert self._features_paths[key] is not None
            features = FeatureSet.load(self._features_paths[key], sep=self.table_sep)
            if keep_loaded:
                self._features[key] = features

        return self._features[key]

    def classes_value(self, key: str, keep_loaded: bool = True):
        if self._classes[key] is None:
            assert self._classes_paths[key] is not None
            classes = ClassInfo.load(self._classes_paths[key], self.table_sep)
            if keep_loaded:
                self._classes[key] = classes

        return self._classes[key]

    def enrollments_value(self, key: str, keep_loaded: bool = True):
        if self._enrollments[key] is None:
            assert self._enrollments_paths[key] is not None
            enrollments = EnrollmentMap.load(
                self._enrollments_paths[key], sep=self.table_sep
            )
            if keep_loaded:
                self._enrollments[key] = enrollments

        return self._enrollments[key]

    def trials_value(self, key: str, keep_loaded: bool = True):
        if self._trials[key] is None:
            assert self._trials_paths[key] is not None
            try:
                if self.sparse_trials:
                    trials = SparseTrialKey.load(self._trials_paths[key])
                else:
                    trials = TrialKey.load(self._trials_paths[key])
            except:
                trials = TrialNdx.load(self._trials_paths[key])

            if keep_loaded:
                self._trials[key] = trials

        return self._trials[key]

    def recordings(self, keep_loaded: bool = True):
        if self._recordings is None:
            yield from ()
        else:
            for key in self._recordings.keys():
                yield key, self.recordings_value(key, keep_loaded)

    def features(self, keep_loaded: bool = True):
        if self._features is None:
            yield from ()
        else:
            for key in self._features.keys():
                yield key, self.features_value(key, keep_loaded)

    def classes(self, keep_loaded: bool = True):
        if self._classes is None:
            yield from ()
        else:
            for key in self._classes.keys():
                yield key, self.classes_value(key, keep_loaded)

    def enrollments(self, keep_loaded: bool = True):
        if self._enrollments is None:
            yield from ()
        else:
            for key in self._enrollments.keys():
                yield key, self.enrollments_value(key, keep_loaded)

    def trials(self, keep_loaded: bool = True):
        if self._trials is None:
            yield from ()
        else:
            for key in self._trials.keys():
                yield key, self.trials_value(key, keep_loaded)

    @staticmethod
    def resolve_dataset_path(dataset_path):
        dataset_path = Path(dataset_path)
        ext = dataset_path.suffix
        if ext in [".yaml", "yml"]:
            dataset_file = dataset_path
            dataset_dir = dataset_path.parent
        else:
            dataset_file = dataset_path / "dataset.yaml"
            dataset_dir = dataset_path

        return dataset_dir, dataset_file

    @staticmethod
    def resolve_file_path(dataset_dir, file_path):
        if file_path.is_file():
            return file_path

        return dataset_dir / file_path

    def save(
        self,
        dataset_path: PathLike,
        update_paths: bool = True,
        table_sep: Optional[str] = None,
    ):
        """Saves all the dataset objects.

        Args:
          dataset_path: str/Path indicating directory 
            to save the dataset or .yaml file to save 
            the dataset info.
          update_paths: whether to update the file_paths in the 
            data structures in the DateSet object

        """
        table_sep = self.table_sep if table_sep is None else table_sep
        if update_paths:
            self.table_sep = table_sep

        table_ext = ".tsv" if table_sep == "\t" else ".csv"
        dataset_dir, dataset_file = Dataset.resolve_dataset_path(dataset_path)
        dataset = {}
        file_name = f"segments{table_ext}"
        dataset["segments"] = file_name
        file_path = dataset_dir / file_name
        self.segments().save(file_path, sep=table_sep)
        if update_paths:
            self._segments_path = file_path

        file_names = {}
        for k, v in self.recordings():
            file_name = k + table_ext
            file_names[k] = file_name
            file_path = dataset_dir / file_name
            v.save(file_path, sep=table_sep)
            if update_paths:
                self._recordings_paths[k] = file_path

        if file_names:
            dataset["recordings"] = file_names

        file_names = {}
        for k, v in self.features():
            file_name = k + table_ext
            file_names[k] = file_name
            file_path = dataset_dir / file_name
            v.save(file_path, sep=table_sep)
            if update_paths:
                self._features_paths[k] = file_path

        if file_names:
            dataset["features"] = file_names

        file_names = {}
        for k, v in self.classes():
            file_name = k + table_ext
            file_names[k] = file_name
            file_path = dataset_dir / file_name
            v.save(file_path, sep=table_sep)
            if update_paths:
                self._classes_paths[k] = file_path

        if file_names:
            dataset["classes"] = file_names

        file_names = {}
        for k, v in self.enrollments():
            file_name = k + table_ext
            file_names[k] = file_name
            file_path = dataset_dir / file_name
            v.save(file_path, sep=table_sep)
            if update_paths:
                self._enrollments_paths[k] = file_path

        if file_names:
            dataset["enrollments"] = file_names

        file_names = {}
        for k, v in self.trials():
            file_name = k + table_ext
            file_names[k] = file_name
            file_path = dataset_dir / file_name
            v.save(file_path)
            if update_paths:
                self._trials_paths[k] = file_path

        if file_names:
            dataset["trials"] = file_names

        with open(dataset_file, "w") as f:
            yaml.dump(dataset, f)

    def update_from_disk(self):
        self.segments()
        for k, v in self.recordings():
            pass

        for k, v in self.features():
            pass

        for k, v in self.classes():
            pass

        for k, v in self.enrollments():
            pass

        for k, v in self.trials():
            pass

    @classmethod
    def load(
        cls, dataset_path: PathLike, lazy: bool = True, sparse_trials: bool = False
    ):
        """Loads all the dataset objects.

        Args:
         dataset_path: str/Path indicating directory 
          to save the dataset or .yaml file to save 
          the dataset info.
         lazy: load data structures lazily when they are needed.
         sparse_trials: load trial keys using the SparseTrialKey class instead of TrialKey class

        """
        dataset_dir, dataset_file = Dataset.resolve_dataset_path(dataset_path)
        with open(dataset_file, "w") as f:
            dataset = yaml.safe_load(f)

        assert "segments" in dataset
        segments = Dataset.resolve_file_path(dataset_dir, dataset["segments"])
        classes = None
        recordings = None
        features = None
        enrollments = None
        trials = None
        if "classes" in dataset:
            classes = {}
            for k, v in dataset["classes"]:
                classes[k] = Dataset.resolve_file_path(dataset_dir, v)

        if "recordings" in dataset:
            recordings = {}
            for k, v in dataset["recordings"]:
                recordings[k] = Dataset.resolve_file_path(dataset_dir, v)

        if "features" in dataset:
            features = {}
            for k, v in dataset["features"]:
                features[k] = Dataset.resolve_file_path(dataset_dir, v)

        if "enrollments" in dataset:
            enrollments = {}
            for k, v in dataset["enrollments"]:
                enrollments[k] = Dataset.resolve_file_path(dataset_dir, v)

        if "trials" in dataset:
            trials = {}
            for k, v in dataset["trials"]:
                trials[k] = Dataset.resolve_file_path(dataset_dir, v)

        dataset = cls(
            segments,
            classes,
            recordings,
            features,
            enrollments,
            trials,
            sparse_trials=sparse_trials,
        )
        if not lazy:
            dataset.update_from_disk()

        return dataset

        # dataset_dir, dataset_file = Dataset.resolve_dataset_path(dataset_path)
        # with open(dataset_file, "w") as f:
        #     dataset = yaml.safe_load(f)

        # assert "segments" in dataset
        # segments = SegmentSet.load(
        #     Dataset.resolve_file_path(dataset_dir, dataset["segments"])
        # )
        # classes = None
        # recordings = None
        # features = None
        # if "classes" in dataset:
        #     classes = {}
        #     for k, v in dataset["classes"]:
        #         classes[k] = ClassInfo.load(Dataset.resolve_file_path(dataset_dir, v))

        # if "recordings" in dataset:
        #     recordings = {}
        #     for k, v in dataset["recordings"]:
        #         recordings[k] = RecordingSet.load(
        #             Dataset.resolve_file_path(dataset_dir, v)
        #         )

        # if "features" in dataset:
        #     features = {}
        #     for k, v in dataset["features"]:
        #         features[k] = FeatureSet.load(Dataset.resolve_file_path(dataset_dir, v))

        # dataset = cls(segments, classes, recordings, features)
        # if not lazy:
        #     dataset.update_from_disk()
