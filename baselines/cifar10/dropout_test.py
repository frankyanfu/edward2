# coding=utf-8
# Copyright 2020 The Edward2 Authors.
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

"""Tests for ResNet-20 with Monte Carlo dropout."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import dropout  # local file import
import tensorflow.compat.v2 as tf

from tensorflow.python.framework import test_util  # pylint: disable=g-direct-tensorflow-import


@test_util.run_all_in_graph_and_eager_modes
class DropoutTest(tf.test.TestCase):

  def testResNetV1(self):
    tf.random.set_seed(83922)
    dataset_size = 15
    batch_size = 5
    input_shape = (32, 32, 1)
    num_classes = 2

    features = tf.random.normal((dataset_size,) + input_shape)
    coeffs = tf.random.normal([tf.reduce_prod(input_shape), num_classes])
    net = tf.reshape(features, [dataset_size, -1])
    logits = tf.matmul(net, coeffs)
    labels = tf.random.categorical(logits, 1)
    features, labels = self.evaluate([features, labels])
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.repeat().shuffle(dataset_size).batch(batch_size)

    model = dropout.resnet_v1(input_shape=input_shape,
                              depth=8,
                              num_classes=num_classes,
                              l2=0.,
                              dropout_rate=0.01)
    model.compile(
        'adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))
    history = model.fit(dataset,
                        steps_per_epoch=dataset_size // batch_size,
                        epochs=2)

    loss_history = history.history['loss']
    self.assertAllGreaterEqual(loss_history, 0.)
    # TODO(trandustin): Reactivate. Whether the loss goes down after this many
    # steps is noisy, so test fails semi-regularly.
    # self.assertGreater(loss_history[0], loss_history[-1])


if __name__ == '__main__':
  tf.test.main()
