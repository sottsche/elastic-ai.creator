import logging
from pathlib import Path

import torch
import torch.nn as nn

from elasticai.creator.nn.integer.addition import Addition
from elasticai.creator.nn.integer.concatenate import Concatenate
from elasticai.creator.nn.integer.design_creator_module import DesignCreatorModule
from elasticai.creator.nn.integer.grucell.design import GRUCell as GRUCellDesign
from elasticai.creator.nn.integer.hadamardproduct import HadamardProduct
from elasticai.creator.nn.integer.hardsigmoid import HardSigmoid
from elasticai.creator.nn.integer.hardtanh import HardTanh
from elasticai.creator.nn.integer.linear import Linear
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

        self.ihprev_concatenate = Concatenate(
            name=self.name + "_ihprev_concatenate",
            inputs_size=self.inputs_size,
            hidden_size=self.hidden_size,
            num_features=self.inputs_size + self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.z_gate_linear = Linear(
            name=self.name + "_z_gate_linear",
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

        self.r_gate_linear = Linear(
            name=self.name + "_r_gate_linear",
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
        self.rnh_hadamard_product = HadamardProduct(
            name=self.name + "_rnh_hadamard_product",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.ni_linear = Linear(
            name=self.name + "_ni_linear",
            in_features=self.inputs_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.nh_linear = Linear(
            name=self.name + "_nh_linear",
            in_features=self.hidden_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.n_addition = Addition(
            name = self.name + "_n_addition",
            num_features = self.hidden_size,
            num_dimensions = 1,
            quant_bits = self.quant_bits,
            quant_data_dir = self.quant_data_dir,
            device = device,
        )
        self.n_tanh = HardTanh(
            name=self.name + "_n_tanh", 
            quant_bits=self.quant_bits, 
            quant_data_dir=self.quant_data_dir,
            device=device
        )

        self.minus_z_addidtion = Addition(
            name = self.name + "_minuz_z_addition",
            num_features = self.hidden_size,
            num_dimensions = 1,
            quant_bits = self.quant_bits,
            quant_data_dir = self.quant_data_dir,
            device = device,
        )

        self.zhprev_hadamard_product = HadamardProduct(
            name=self.name + "_zhprev_hadamard_product",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.zn_hadamard_product = HadamardProduct(
            name=self.name + "_zn_hadamard_product",
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
        self.math_ops = MathOperations()
        self.precomputed = False

    def create_design(self, name) -> GRUCellDesign:
        return GRUCellDesign(
            name=name,
            data_width=self.quant_bits,
            ihprev_concatenate=self.ihprev_concatenate,
            z_gate_linear=self.z_gate_linear,
            z_sigmoid=self.z_sigmoid,
            r_gate_linear=self.r_gate_linear,
            r_sigmoid=self.r_sigmoid,
            ni_linear=self.ni_linear,
            nh_linear=self.nh_linear,
            rnh_hadamard=self.rnh_hadamard_product,
            n_addition = self.n_addition,
            n_tanh=self.n_tanh,
            minus_z_addition = self.minus_z_addidtion,
            zhprev_hadamard_product=self.zhprev_hadamard_product,
            zn_hadamard_product=self.zn_hadamard_product,
            h_next_addition=self.h_next_addition,
            quantized_one=self.quantized_one,
            work_library_name="work",
        )

    def precompute(self) -> None:
        self.ihprev_concatenate.precompute()
        self.z_gate_linear.precompute()
        self.z_sigmoid.precompute()
        self.r_gate_linear.precompute()
        self.r_sigmoid.precompute()
        self.ni_linear.precompute()
        self.nh_linear.precompute()
        self.rnh_hadamard_product.precompute()
        self.n_addition.precompute()
        self.n_tanh.precompute()
        self.minus_z_addidtion.precompute()
        self.zhprev_hadamard_product.precompute()
        self.zn_hadamard_product.precompute()
        self.h_next_addition.precompute()
############################
        self.quantized_one = self.minus_z_sigmoid_outputs_QParams.quantize(
            torch.tensor(1.0)
        )

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
        self.save_quant_data(
            q_inputs, self.quant_data_dir, f"{self.ihprev_concatenate.name}_q_x_1"
        )
        self.save_quant_data(
            q_h_prev, self.quant_data_dir, f"{self.ihprev_concatenate.name}_q_x_2"
        )
        q_concated_ihprev = self.ihprev_concatenate.int_forward(
            q_inputs1=q_inputs, q_inputs2=q_h_prev
        )
        self.save_quant_data(
            q_concated_ihprev,
            self.quant_data_dir,
            f"{self.ihprev_concatenate.name}_q_y",
        )

        # gate linear transformations and activations
        # update gate
        self.save_quant_data(
            q_concated_ihprev,
            self.quant_data_dir,
            f"{self.z_gate_linear.name}_q_x",
        )
        q_z_gate_outputs = self.z_gate_linear.int_forward(q_inputs=q_concated_ihprev)
        self.save_quant_data(
            q_z_gate_outputs, self.quant_data_dir, f"{self.z_gate_linear.name}_q_y"
        )
        self.save_quant_data(
            q_z_gate_outputs, self.quant_data_dir, f"{self.z_sigmoid.name}_q_x"
        )
        q_z_sigmoid_outputs = self.z_sigmoid.int_forward(q_inputs=q_z_gate_outputs)
        self.save_quant_data(
            q_z_sigmoid_outputs,
            self.quant_data_dir,
            f"{self.z_sigmoid.name}_q_y",
        )

        # reset gate
        self.save_quant_data(
            q_concated_ihprev,
            self.quant_data_dir,
            f"{self.r_gate_linear.name}_q_x",
        )
        q_r_gate_outputs = self.r_gate_linear.int_forward(q_inputs=q_concated_ihprev)
        self.save_quant_data(
            q_r_gate_outputs, self.quant_data_dir, f"{self.r_gate_linear.name}_q_y"
        )
        self.save_quant_data(
            q_r_gate_outputs, self.quant_data_dir, f"{self.r_sigmoid.name}_q_x"
        )
        q_r_sigmoid_outputs = self.r_sigmoid.int_forward(q_inputs=q_r_gate_outputs)
        self.save_quant_data(
            q_r_sigmoid_outputs,
            self.quant_data_dir,
            f"{self.r_sigmoid.name}_q_y",
        )

        #ni_linear
        self.save_quant_data(
            q_inputs, self.quant_data_dir, f"{self.ni_linear.name}_q_x",
        )
        q_ni_gate_outputs = self.ni_linear.int_forward(q_inputs=q_inputs)

        self.save_quant_data(
            q_ni_gate_outputs, self.quant_data_dir, f"{self.ni_linear.name}_q_y",
        )

        #nh_linear
        self.save_quant_data(
            q_h_prev, self.quant_data_dir, f"{self.nh_linear.name}_q_x",
        )
        q_nh_gate_outputs = self.nh_linear.int_forward(q_inputs=q_h_prev)

        self.save_quant_data(
            q_nh_gate_outputs, self.quant_data_dir, f"{self.nh_linear.name}_q_y",
        )

        #rnh_hadamard_product
        self.save_quant_data(
            q_nh_gate_outputs, self.quant_data_dir, f"{self.rnh_hadamard_product.name}_q_x_1",
        )
        self.save_quant_data(
            q_r_sigmoid_outputs, self.quant_data_dir, f"{self.rnh_hadamard_product.name}_q_x_2",
        )
        q_rnh_hadamard_product_outputs = self.rnh_hadamard_product.int_forward(
            q_inputs1=q_nh_gate_outputs,
            q_inputs2=q_r_sigmoid_outputs
        )
        self.save_quant_data(
            q_rnh_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.rnh_hadamard_product.name}_q_y"
        )

        #n_addition
        self.save_quant_data(
            q_ni_gate_outputs,
            self.quant_data_dir,
            f"{self.n_addition.name}_q_x_1",
        )
        self.save_quant_data(
            q_rnh_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.n_addition.name}_q_x_2",
        )
        q_n_addition_outputs = self.n_addition.int_forward(
            q_inputs1=q_ni_gate_outputs,
            q_inputs2=q_rnh_hadamard_product_outputs
        )
        self.save_quant_data(
            q_n_addition_outputs,
            self.quant_data_dir,
            f"{self.n_addition.name}_q_y"
        )

        #n_tanh
        self.save_quant_data(
            q_n_addition_outputs, self.quant_data_dir, f"{self.n_tanh.name}_q_x"
        )
        q_n_tanh_outputs = self.n_tanh.int_forward(q_inputs=q_n_addition_outputs)
        self.save_quant_data(
            q_n_tanh_outputs, self.quant_data_dir, f"{self.n_tanh.name}_q_y"
        )

        #minus_z_addition
        self.save_quant_data(
            self.quantized_one,
            self.quant_data_dir,
            f"{self.minus_z_addidtion.name}_q_x_1"
        )
        self.save_quant_data(
            q_z_sigmoid_outputs,
            self.quant_data_dir,
            f"{self.minus_z_addidtion.name}_q_x_2"
        )
        q_minus_z_addition_outputs = self.math_ops.intsub(self.quantized_one, q_z_sigmoid_outputs, self.z_sigmoid.quant_bits + 1)

        self.save_quant_data(
            q_minus_z_addition_outputs,
            self.quant_data_dir,
            f"{self.minus_z_addidtion.name}_q_y"
        )

        #zn_hadamard_product
        self.save_quant_data(
            q_minus_z_addition_outputs,
            self.quant_data_dir,
            f"{self.zn_hadamard_product.name}_q_x_1"
        )
        self.save_quant_data(
            q_n_tanh_outputs,
            self.quant_data_dir,
            f"{self.zn_hadamard_product.name}_q_x_2"
        )
        q_zn_hadamard_product_outputs = self.zn_hadamard_product.int_forward(
            q_inputs1=q_minus_z_addition_outputs,
            q_inputs2=q_n_tanh_outputs
        )
        self.save_quant_data(
            q_zn_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.zn_hadamard_product.name}_q_y"
        )

        #zh_hadamard_product
        self.save_quant_data(
            q_z_sigmoid_outputs,
            self.quant_data_dir,
            f"{self.zhprev_hadamard_product.name}_q_x_1"
        )
        self.save_quant_data(
            q_h_prev,
            self.quant_data_dir,
            f"{self.zhprev_hadamard_product.name}_q_x_2"
        )
        q_zhprev_hadamard_product_outputs = self.zhprev_hadamard_product.int_forward(
            q_inputs1=q_z_sigmoid_outputs,
            q_inputs2=q_h_prev
        )
        self.save_quant_data(
            q_zhprev_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.zhprev_hadamard_product.name}_q_y"
        )

        #h_next_addition
        self.save_quant_data(
            q_zn_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.h_next_addition.name}_q_x_1"
        )
        self.save_quant_data(
            q_zhprev_hadamard_product_outputs,
            self.quant_data_dir,
            f"{self.h_next_addition.name}._q_x_2"
        )
        q_h_next = self.h_next_addition.int_forward(
            q_inputs1=q_zn_hadamard_product_outputs,
            q_inputs2=q_zhprev_hadamard_product_outputs
        )
        self.save_quant_data(
            q_h_next,
            self.quant_data_dir,
            f"{self.h_next_addition.name}_q_y"
        )

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
        
        # concatenate inputs and h_prev
        concated_ihprev = self.ihprev_concatenate.forward(
            inputs1=inputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.inputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )

        # gate linear transformations and activations
        z_gate_outputs = self.z_gate_linear.forward(
            inputs=concated_ihprev,
            given_inputs_QParams=self.ihprev_concatenate.outputs_QParams,
        )

        z_sigmoid_outputs = self.z_sigmoid.forward(
            inputs=z_gate_outputs,
            given_inputs_QParams=self.z_gate_linear.outputs_QParams,
        )

        r_gate_outputs = self.r_gate_linear.forward(
            inputs=concated_ihprev,
            given_inputs_QParams=self.ihprev_concatenate.outputs_QParams,
        )

        r_sigmoid_outputs = self.r_sigmoid.forward(
            inputs=r_gate_outputs,
            given_inputs_QParams=self.r_gate_linear.outputs_QParams,
        )

        ni_linear_outputs = self.ni_linear.forward(
            inputs=inputs,
            given_inputs_QParams=self.inputs_QParams
        )

        nh_linear_outputs = self.nh_linear.forward(
            inputs=h_prev,
            given_inputs_QParams=self.h_prev_QParams
        )

        rnh_hadamard_product_outputs = self.rnh_hadamard_product.forward(
            inputs1=nh_linear_outputs,
            inputs2=r_sigmoid_outputs,
            given_inputs1_QParams=self.nh_linear.outputs_QParams,
            given_inputs2_QParams=self.r_sigmoid.outputs_QParams
        )

        n_addition_outputs = self.n_addition.forward(
            inputs1=ni_linear_outputs,
            inputs2=rnh_hadamard_product_outputs,
            given_inputs1_QParams=self.ni_linear.outputs_QParams,
            given_inputs2_QParams=self.rnh_hadamard_product.outputs_QParams
        )

        n_tanh_outputs = self.n_tanh.forward(
            inputs=n_addition_outputs,
            given_inputs_QParams=self.n_addition.outputs_QParams
        )

        h_next_inputs1 = self.zhprev_hadamard_product.forward(
            inputs1=z_sigmoid_outputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.z_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )

        minus_z_sigmoid_outputs = 1 - z_sigmoid_outputs
        self.minus_z_sigmoid_outputs_QParams.update_quant_params(
            minus_z_sigmoid_outputs
        )
        minus_z_sigmoid_outputs = SimQuant.apply(
            minus_z_sigmoid_outputs, self.minus_z_sigmoid_outputs_QParams
        )

        h_next_inputs2 = self.zn_hadamard_product.forward(
            inputs1=minus_z_sigmoid_outputs,
            inputs2=n_tanh_outputs,
            given_inputs1_QParams=self.z_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.n_tanh.outputs_QParams,
        )
        h_next = self.h_next_addition.forward(
            inputs1=h_next_inputs1,
            inputs2=h_next_inputs2,
            given_inputs1_QParams=self.zhprev_hadamard_product.outputs_QParams,
            given_inputs2_QParams=self.zn_hadamard_product.outputs_QParams,
        )

        self.h_next_QParams = self.h_next_addition.outputs_QParams
        c_next = None
        return h_next, c_next
