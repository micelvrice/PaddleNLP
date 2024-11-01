# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import sys
import unittest
from parameterized import parameterized_class

from tests.testing_utils import argv_context_guard, load_test_config

from .testing_utils import LLMTest


@parameterized_class(
    ["model_dir"],
    [
        ["llama"],
        ["qwen2"],
    ],
)
class FinetuneTest(LLMTest, unittest.TestCase):
    config_path: str = "./tests/fixtures/llm/longlora.yaml"
    model_dir: str = None

    def setUp(self) -> None:
        LLMTest.setUp(self)

        sys.path.insert(0, self.model_dir)

    def tearDown(self) -> None:
        LLMTest.tearDown(self)

    def test_finetune(self):
        finetune_config = load_test_config(self.config_path, "finetune", self.model_dir)
        if finetune_config["autoregressive"]:
            finetune_config["dataset_name_or_path"] = "./tests/fixtures/llm/autoregressive_data/"
        else:
            finetune_config["dataset_name_or_path"] = self.data_dir
        finetune_config["output_dir"] = self.output_dir
        with argv_context_guard(finetune_config):
            from run_finetune import main

            main()
