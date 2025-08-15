import logging
from pathlib import Path

import torch
import torch.nn as nn

from elasticai.creator.nn.integer.addition import Addition
from elasticai.creator.nn.integer.subtraction import Subtraction
from elasticai.creator.nn.integer.concatenate import Concatenate
from elasticai.creator.nn.integer.design_creator_module import DesignCreatorModule
from elasticai.creator.nn.integer.grucell.design_rh import GRUCell as GRUCellDesign
from elasticai.creator.nn.integer.hadamardproduct import HadamardProduct
from elasticai.creator.nn.integer.hardsigmoid import HardSigmoid
from elasticai.creator.nn.integer.hardtanh import HardTanh
from elasticai.creator.nn.integer.linear import Linear 
from elasticai.creator.nn.integer.linear.linear_with_subtraction import LinearWithSubtraction
from elasticai.creator.nn.integer.math_operations.math_operations import MathOperations
from elasticai.creator.nn.integer.quant_utils.Observers import GlobalMinMaxObserver
from elasticai.creator.nn.integer.quant_utils.QParams import AsymmetricSignedQParams
from elasticai.creator.nn.integer.quant_utils.SimQuant import SimQuant


class GRUCell(DesignCreatorModule, nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        self.inputs_size = kwargs.get("inputs_size")
        self.hidden_size = kwargs.get("hidden_size")
        self.window_size = kwargs.get("window_size")

        self.name = kwargs.get("name")
        self.quant_bits = kwargs.get("quant_bits")
        self.quant_data_dir = kwargs.get("quant_data_dir")
        device = kwargs.get("device")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.concatenate = Concatenate(
            name=self.name + "_concatenate",
            inputs_size=self.inputs_size,
            hidden_size=self.hidden_size,
            num_features=self.inputs_size + self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.z_linear = Linear(
            name=self.name + "_z_linear",
            in_features=self.inputs_size + self.hidden_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.z_sigmoid = HardSigmoid(
            name=self.name + "_z_sigmoid", 
            quant_bits=self.quant_bits,
            quant_data_dir = self.quant_data_dir,
            device=device
        )

        self.r_linear = Linear(
            name=self.name + "_r_linear",
            in_features=self.inputs_size + self.hidden_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.r_sigmoid = HardSigmoid(
            name=self.name + "_r_sigmoid", 
            quant_bits=self.quant_bits, 
            quant_data_dir=self.quant_data_dir,
            device=device
        )
        self.rh_hadamard = HadamardProduct(
            name=self.name + "_rh_hadamard",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.concatenate_n = Concatenate(
            name=self.name + "_concatenate_n",
            inputs_size=self.inputs_size,
            hidden_size=self.hidden_size,
            num_features=self.inputs_size + self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.n_linear = Linear(
            name=self.name + "_n_linear",
            in_features=self.inputs_size + self.hidden_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.n_tanh = HardTanh(
            name=self.name + "_n_tanh", 
            quant_bits=self.quant_bits, 
            quant_data_dir=self.quant_data_dir,
            device=device
        )
        self.one_minus_z = Subtraction(
            name=self.name + "_one_minus_z",
            num_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )

        self.zH_hadamard = HadamardProduct(
            name=self.name + "_zH_hadamard",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.zN_hadamard = HadamardProduct(
            name=self.name + "_zN_hadamard",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )

        self.h_next_addition = Addition(
            name=self.name + "_h_next_addition",
            num_features=self.hidden_size,
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )

        self.inputs_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        self.h_prev_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        self.h_next_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        self.minus_z_sigmoid_outputs_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        ####Only for rnncell interface####
        self.c_next_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        self.precomputed = False

    def create_design(self, name) -> GRUCellDesign:
        return GRUCellDesign(
            name=name,
            data_width=self.quant_bits,
            concatenate=self.concatenate,
            f_linear=self.z_linear,
            f_sigmoid=self.z_sigmoid,
            r_linear=self.r_linear,
            r_sigmoid=self.r_sigmoid,
            fh_hadamard=self.rh_hadamard,
            concatenate_n=self.concatenate_n,
            n_linear=self.n_linear,
            n_tanh=self.n_tanh,
            one_minus_f=self.one_minus_z,
            fH_hadamard=self.zH_hadamard,
            fN_hadamard=self.zN_hadamard,
            h_next_addition=self.h_next_addition,
            quantized_one=self.quantized_one[0].item(),
            work_library_name="work",
        )

    def precompute(self) -> None:
        self.concatenate.precompute()
        self.z_linear.precompute()
        self.z_sigmoid.precompute()
        self.r_linear.precompute()
        self.r_sigmoid.precompute()
        self.rh_hadamard.precompute()
        self.concatenate_n.precompute()
        self.n_linear.precompute()
        self.n_tanh.precompute()
        self.one_minus_z.precompute()
        self.zH_hadamard.precompute()
        self.zN_hadamard.precompute()
        self.h_next_addition.precompute()
        # self.minus_z_subtraction.inputs1_QParams.update_quant_params(torch.tensor(1.0))
        # self.quantized_one = self.z_sigmoid.quantized_one
        self.quantized_one = self.z_sigmoid.outputs_QParams.quantize(
            torch.tensor(1.0, dtype=torch.float32)
        )
############################

        self.precomputed = True

    def save_quant_data(self, tensor, file_dir: Path, file_name: str):
        file_path = Path(file_dir) / f"{file_name}.txt"
        tensor_str = "\n".join(map(str, tensor.flatten().tolist()))
        file_path.write_text(tensor_str)

    def int_forward(
        self,
        q_inputs: torch.IntTensor,
        q_h_prev: torch.IntTensor,
        q_c_prev: torch.IntTensor = None,
    ) -> torch.IntTensor:
        assert not self.training, "int_forward should be called in eval mode"
        assert self.precomputed, "precompute should be called before int_forward"
        self.save_quant_data(q_inputs, self.quant_data_dir, f"{self.name}_q_x_1")
        self.save_quant_data(q_h_prev, self.quant_data_dir, f"{self.name}_q_x_2")

        # concatenate inputs and h_prev
        q_concated_ihprev = self.concatenate.int_forward(
            q_inputs1=q_inputs, q_inputs2=q_h_prev
        )

        # gate linear transformations and activations
        # update gate
        q_z_linear_outputs = self.z_linear.int_forward(q_inputs=q_concated_ihprev)
        q_z_sigmoid_outputs = self.z_sigmoid.int_forward(q_inputs=q_z_linear_outputs)

        # reset gate
        q_r_linear_outputs = self.r_linear.int_forward(q_inputs=q_concated_ihprev)
        q_r_sigmoid_outputs = self.r_sigmoid.int_forward(q_inputs=q_r_linear_outputs)

        #rh_hadamard_product
        q_rh_hadamard_outputs = self.rh_hadamard.int_forward(
            q_inputs1=q_r_sigmoid_outputs,
            q_inputs2=q_h_prev,
        )
        q_n_concated = self.concatenate_n.int_forward(
            q_inputs1= q_inputs,
            q_inputs2= q_rh_hadamard_outputs,
        )

        #ni_linear
        q_n_linear_outputs = self.n_linear.int_forward(q_inputs=q_n_concated)

        #n_tanh
        q_n_tanh_outputs = self.n_tanh.int_forward(q_inputs=q_n_linear_outputs)

        #one_minus_z
        q_one_minus_z_outputs = self.one_minus_z.int_forward(
            q_inputs1=self.z_sigmoid.outputs_QParams.quantize(torch.tensor(1)),
            q_inputs2=q_z_sigmoid_outputs
        )

        
        #zn_hadamard_product
        q_zN_hadamard_outputs = self.zN_hadamard.int_forward(
            q_inputs1=q_one_minus_z_outputs,
            q_inputs2=q_n_tanh_outputs
        )

        #zh_hadamard_product
        q_zH_hadamard_outputs = self.zH_hadamard.int_forward(
            q_inputs1=q_z_sigmoid_outputs,
            q_inputs2=q_h_prev
        )

        #h_next_addition
        q_h_next = self.h_next_addition.int_forward(
            q_inputs1=q_zN_hadamard_outputs,
            q_inputs2=q_zH_hadamard_outputs
        )
               
        self.save_quant_data(
            q_h_next,
            self.quant_data_dir,
            f"{self.name}_q_y_1"
        )
        self.save_quant_data(
            q_h_next,
            self.quant_data_dir,
            f"{self.name}_q_y")

        q_c_next = None

        return q_h_next, q_c_next

    def forward(
        self,
        inputs: torch.FloatTensor,
        h_prev: torch.FloatTensor,
        given_inputs_QParams: torch.nn.Module,
        c_prev: torch.FloatTensor = None,
    ) -> torch.Tensor:
        self.inputs_QParams = given_inputs_QParams

        if self.training:
            self.h_prev_QParams.update_quant_params(h_prev)
            self.z_sigmoid.outputs_QParams.update_quant_params(
                torch.tensor(1.0, dtype=torch.float32)
            )
        
        # concatenate inputs and h_prev
        concatenated = self.concatenate.forward(
            inputs1=inputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.inputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )

        # gate linear transformations and activations
        z_linear_outputs = self.z_linear.forward(
            inputs=concatenated,
            given_inputs_QParams=self.concatenate.outputs_QParams,
        )

        z_sigmoid_outputs = self.z_sigmoid.forward(
            inputs=z_linear_outputs,
            given_inputs_QParams=self.z_linear.outputs_QParams,
        )

        r_linear_outputs = self.r_linear.forward(
            inputs=concatenated,
            given_inputs_QParams=self.concatenate.outputs_QParams,
        )

        r_sigmoid_outputs = self.r_sigmoid.forward(
            inputs=r_linear_outputs,
            given_inputs_QParams=self.r_linear.outputs_QParams,
        )
        rh_hadamard_outputs = self.rh_hadamard.forward(
            inputs1=r_sigmoid_outputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.r_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )
        n_concatenated = self.concatenate_n.forward(
            inputs1=inputs,
            inputs2=rh_hadamard_outputs,
            given_inputs1_QParams=self.inputs_QParams,
            given_inputs2_QParams=self.rh_hadamard.outputs_QParams,
        )
        n_linear_outputs = self.n_linear.forward(
            inputs=n_concatenated,
            given_inputs_QParams=self.concatenate_n.outputs_QParams,
        )

        n_tanh_outputs = self.n_tanh.forward(
            inputs=n_linear_outputs,
            given_inputs_QParams=self.n_linear.outputs_QParams
        )

        #self.h_prev_QParams.update_quant_params(torch.tensor(3.0, dtype=torch.float32))
        #self.h_prev_QParams.update_quant_params(torch.tensor(-3.0, dtype=torch.float32))
        zH_hadamard_outputs = self.zH_hadamard.forward(
            inputs1=z_sigmoid_outputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.z_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )
        one_minus_z_outputs = self.one_minus_z.forward(
            inputs1=torch.tensor(1),
            inputs2=z_sigmoid_outputs,
            given_inputs1_QParams=self.z_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.z_sigmoid.outputs_QParams,
        )
        
        zN_hadamard_outputs = self.zN_hadamard.forward(
            inputs1=one_minus_z_outputs,
            inputs2=n_tanh_outputs,
            given_inputs1_QParams=self.one_minus_z.outputs_QParams,
            given_inputs2_QParams=self.n_tanh.outputs_QParams,
        )
        h_next = self.h_next_addition.forward(
            inputs1=zN_hadamard_outputs,
            inputs2=zH_hadamard_outputs,
            given_inputs1_QParams=self.zN_hadamard.outputs_QParams,
            given_inputs2_QParams=self.zH_hadamard.outputs_QParams,
        )

        self.h_next_QParams = self.h_next_addition.outputs_QParams
        c_next = None
        return h_next, c_next
