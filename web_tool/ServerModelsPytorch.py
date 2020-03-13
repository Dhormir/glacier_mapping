#!/usr/bin/env python3
from ServerModelsAbstract import BackendModel
import numpy as np
import torch
import pathlib


class PytorchUNet(BackendModel):
    def __init__(self, gpuid, verbose=False, model_path=None):
        if model_path is None:
            model_path = pathlib.Path("web_tool", "data", "model_188.pt")

        if torch.cuda.is_available():
            self.model = torch.load(model_path)
        else:
            self.model = torch.load(model_path, map_location=torch.device("cpu"))
        self.verbose = verbose


    def run(self, input_data, extent, on_tile=False):
        """
        makes predictions given
        """
        print("running")
        output, output_features = self.run_model_on_tile(input_data)
        return output

    def run_model_on_batch(self, batch_data, batch_size=32, predict_central_pixel_only=False):
        """ Expects batch_data to have shape (none, 240, 240, 4) and have values in the [0, 255] range.
        """
        print("running batch")
        batch_data = batch_data / 255.0
        output = self.model.predict(batch_data, batch_size=batch_size, verbose=0)
        output, output_features = output
        output = output[:,:,:,1:]

        if self.augment_model_trained:
            num_samples, height, width, num_features = output_features.shape

            if predict_central_pixel_only:
                output_features = output_features[:,120,120,:].reshape(-1, num_features)
                output = self.augment_model.predict_proba(output_features)
                output = output.reshape(num_samples, 4)
            else:
                output_features = output_features.reshape(-1, num_features)
                output = self.augment_model.predict_proba(output_features)
                output = output.reshape(num_samples, height, width, 4)
        else:
            if predict_central_pixel_only:
                output = output[:,120,120,:]

        return output

    def retrain(self, **kwargs):
        x_train = np.concatenate(self.augment_x_train, axis=0)
        y_train = np.concatenate(self.augment_y_train, axis=0)

        vals, counts = np.unique(y_train, return_counts=True)

        if len(vals) >= 4:
            self.augment_model.fit(x_train, y_train)
            print("fine-tuning accuracy: ",self.augment_model.score(x_train, y_train))
            self.augment_model_trained = True
            self.undo_stack.append("retrain")

            success = True
            message = "Fit accessory model with %d samples" % (x_train.shape[0])
        else:
            success = False
            message = "Need to include training samples from each class"

        return success, message

    def add_sample(self, tdst_row, bdst_row, tdst_col, bdst_col, class_idx):
        x_features = self.current_features[tdst_row:bdst_row+1, tdst_col:bdst_col+1, :].copy().reshape(-1, self.current_features.shape[2])
        y_samples = np.zeros((x_features.shape[0]), dtype=np.uint8)
        y_samples[:] = class_idx
        self.augment_x_train.append(x_features)
        self.augment_y_train.append(y_samples)
        self.undo_stack.append("sample")

    def undo(self):
        num_undone = 0
        if len(self.undo_stack) > 0:
            undo = self.undo_stack.pop()
            if undo == "sample":
                self.augment_x_train.pop()
                self.augment_y_train.pop()
                num_undone += 1
                success = True
                message = "Undoing sample"
            elif undo == "retrain":
                while self.undo_stack[-1] == "retrain":
                    self.undo_stack.pop()
                self.augment_x_train.pop()
                self.augment_y_train.pop()
                num_undone += 1
                success = True
                message = "Undoing sample"
            else:
                raise ValueError("This shouldn't happen")
        else:
            success = False
            message = "Nothing to undo"
        return success, message, num_undone

    def reset(self):
        self.augment_x_train = []
        self.augment_y_train = []
        self.undo_stack = []
        self.augment_model = sklearn.base.clone(KerasDenseFineTune.AUGMENT_MODEL)
        self.augment_model_trained = False

        for row in self.augment_base_x_train:
            self.augment_x_train.append(row)
        for row in self.augment_base_y_train:
            self.augment_y_train.append(row)

        if self.use_seed_data:
            self.retrain()

    def run_model_on_tile(self, naip_tile, batch_size=32):
        """ Expects naip_tile to have shape (height, width, channels) and have values in the [0, 1] range.
        """
        print("running on tile")
        height = naip_tile.shape[0]
        width = naip_tile.shape[1]

        output = np.zeros((height, width, self.output_channels), dtype=np.float32)
        output_features = np.zeros((height, width, self.output_features), dtype=np.float32)

        counts = np.zeros((height, width), dtype=np.float32) + 0.000000001
        kernel = np.ones((self.input_size, self.input_size), dtype=np.float32) * 0.1
        kernel[10:-10, 10:-10] = 1
        kernel[self.down_weight_padding:self.down_weight_padding+self.stride_y,
               self.down_weight_padding:self.down_weight_padding+self.stride_x] = 5

        batch = []
        batch_indices = []
        batch_count = 0

        for y_index in (list(range(0, height - self.input_size, self.stride_y)) + [height - self.input_size,]):
            for x_index in (list(range(0, width - self.input_size, self.stride_x)) + [width - self.input_size,]):
                naip_im = naip_tile[y_index:y_index+self.input_size, x_index:x_index+self.input_size, :]

                batch.append(naip_im)
                batch_indices.append((y_index, x_index))
                batch_count+=1


        model_output = self.model.predict(np.array(batch), batch_size=batch_size, verbose=0)

        for i, (y, x) in enumerate(batch_indices):
            output[y:y+self.input_size, x:x+self.input_size] += model_output[0][i] * kernel[..., np.newaxis]
            output_features[y:y+self.input_size, x:x+self.input_size] += model_output[1][i] * kernel[..., np.newaxis]
            counts[y:y+self.input_size, x:x+self.input_size] += kernel

        output = output / counts[..., np.newaxis]
        output = output[:,:,1:5]
        output_features = output_features / counts[..., np.newaxis]

        return output, output_features
