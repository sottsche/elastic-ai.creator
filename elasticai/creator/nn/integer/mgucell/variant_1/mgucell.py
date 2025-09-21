import logging
from pathlib import Path

import torch
import torch.nn as nn

from elasticai.creator.nn.integer.addition import Addition
from elasticai.creator.nn.integer.subtraction import Subtraction
from elasticai.creator.nn.integer.concatenate import Concatenate
from elasticai.creator.nn.integer.design_creator_module import DesignCreatorModule
from elasticai.creator.nn.integer.mgucell.variant_1.design import MGUCell as MGUCellDesign
from elasticai.creator.nn.integer.hadamardproduct import HadamardProduct
from elasticai.creator.nn.integer.hardsigmoid import HardSigmoid
from elasticai.creator.nn.integer.hardtanh import HardTanh
from elasticai.creator.nn.integer.linear import Linear 
from elasticai.creator.nn.integer.math_operations.math_operations import MathOperations
from elasticai.creator.nn.integer.quant_utils.Observers import GlobalMinMaxObserver
from elasticai.creator.nn.integer.quant_utils.QParams import AsymmetricSignedQParams
from elasticai.creator.nn.integer.quant_utils.SimQuant import SimQuant


class MGUCell(DesignCreatorModule, nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        self.inputs_size = kwargs.get("inputs_size")
        self.hidden_size = kwargs.get("hidden_size")
        self.window_size = kwargs.get("window_size")

        self.name = kwargs.get("name")
        self.quant_bits = kwargs.get("quant_bits")
        self.quant_data_dir = kwargs.get("quant_data_dir")
        device = kwargs.get("device")
        self.use_parallelised_template = kwargs.get("use_parallelised_template", False)
        self.unroll_factor = kwargs.get("unroll_factor", 1)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.f_linear = Linear(
            name=self.name + "_f_linear",
            in_features=self.hidden_size,
            use_parallelised_template=self.use_parallelised_template,
            unroll_factor=self.unroll_factor,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.f_sigmoid = HardSigmoid(
            name=self.name + "_f_sigmoid", 
            quant_bits=self.quant_bits,
            quant_data_dir = self.quant_data_dir,
            device=device
        )

        self.fh_hadamard = HadamardProduct(
            name=self.name + "_fh_hadamard",
            num_features=self.hidden_size,  # TODO: check this
            num_dimensions=1,  # TODO: check this
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.fh_linear = Linear(
            name=self.name + "_fh_linear",
            use_parallelised_template=self.use_parallelised_template,
            unroll_factor=self.unroll_factor,
            in_features=self.hidden_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.ni_linear = Linear(
            name=self.name + "_ni_linear",
            use_parallelised_template=self.use_parallelised_template and self.inputs_size > 1,
            unroll_factor=self.unroll_factor,
            in_features=self.inputs_size,
            out_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
            bias=True,
        )
        self.n_addition = Addition(
            name=self.name + "_n_addition",
            num_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )
        self.n_tanh = HardTanh(
            name=self.name + "_n_tanh", 
            quant_bits=self.quant_bits, 
            quant_data_dir=self.quant_data_dir,
            device=device
        )
        self.one_minus_f = Subtraction(
            name=self.name + "_one_minus_f",
            num_features=self.hidden_size,
            num_dimensions=1,
            quant_bits=self.quant_bits,
            quant_data_dir=self.quant_data_dir,
            device=device,
        )

        self.fN_hadamard = HadamardProduct(
            name=self.name + "_fN_hadamard",
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
        self.minus_f_sigmoid_outputs_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        ####Only for rnncell interface####
        self.c_next_QParams = AsymmetricSignedQParams(
            quant_bits=self.quant_bits, observer=GlobalMinMaxObserver()
        ).to(device)
        self.precomputed = False

    def create_design(self, name) -> MGUCellDesign:
        return MGUCellDesign(
            name=name,
            data_width=self.quant_bits,
            f_linear=self.f_linear,
            f_sigmoid=self.f_sigmoid,
            fh_hadamard=self.fh_hadamard,
            fh_linear=self.fh_linear,
            ni_linear=self.ni_linear,
            n_addition=self.n_addition,
            n_tanh=self.n_tanh,
            one_minus_f=self.one_minus_f,
            fN_hadamard=self.fN_hadamard,
            h_next_addition=self.h_next_addition,
            quantized_one=self.quantized_one[0].item(),
            work_library_name="work",
        )

    def precompute(self) -> None:
        self.f_linear.precompute()
        self.f_sigmoid.precompute()
        self.fh_hadamard.precompute()
        self.ni_linear.precompute()
        self.fh_linear.precompute()
        self.n_addition.precompute()
        self.n_tanh.precompute()
        self.one_minus_f.precompute()
        self.fN_hadamard.precompute()
        self.h_next_addition.precompute()
        # self.minus_z_subtraction.inputs1_QParams.update_quant_params(torch.tensor(1.0))
        # self.quantized_one = self.z_sigmoid.quantized_one
        self.quantized_one = self.f_sigmoid.outputs_QParams.quantize(
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

        # gate linear transformations and activations
        # update gate
        q_f_linear_outputs = self.f_linear.int_forward(q_inputs=q_h_prev)
        q_f_sigmoid_outputs = self.f_sigmoid.int_forward(q_inputs=q_f_linear_outputs)

        #rh_hadamard_product
        q_fh_hadamard_outputs = self.fh_hadamard.int_forward(
            q_inputs1=q_f_sigmoid_outputs,
            q_inputs2=q_h_prev,
        )

        #ni_linear
        q_ni_linear_outputs = self.ni_linear.int_forward(q_inputs=q_inputs)
        q_fh_linear_outputs = self.fh_linear.int_forward(q_inputs=q_fh_hadamard_outputs)

        #n_addition
        q_n_linear_outputs = self.n_addition.int_forward(
            q_inputs1=q_ni_linear_outputs,
            q_inputs2=q_fh_linear_outputs
        )
        #n_tanh
        q_n_tanh_outputs = self.n_tanh.int_forward(q_inputs=q_n_linear_outputs)

        #one_minus_f
        q_one_minus_f_outputs = self.one_minus_f.int_forward(
            q_inputs1=self.quantized_one,
            q_inputs2=q_f_sigmoid_outputs
        )

        
        #fn_hadamard_product
        q_fN_hadamard_outputs = self.fN_hadamard.int_forward(
            q_inputs1=q_one_minus_f_outputs,
            q_inputs2=q_n_tanh_outputs
        )

        #fh_hadamard_product

        #h_next_addition
        q_h_next = self.h_next_addition.int_forward(
            q_inputs1=q_fN_hadamard_outputs,
            q_inputs2=q_fh_hadamard_outputs
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
            self.f_sigmoid.outputs_QParams.update_quant_params(
                torch.tensor(1.0, dtype=torch.float32)
            )

        # gate linear transformations and activations
        f_linear_outputs = self.f_linear.forward(
            inputs=h_prev,
            given_inputs_QParams=self.h_prev_QParams,
        )

        f_sigmoid_outputs = self.f_sigmoid.forward(
            inputs=f_linear_outputs,
            given_inputs_QParams=self.f_linear.outputs_QParams,
        )

        fh_hadamard_outputs = self.fh_hadamard.forward(
            inputs1=f_sigmoid_outputs,
            inputs2=h_prev,
            given_inputs1_QParams=self.f_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.h_prev_QParams,
        )
        fh_linear_outputs = self.fh_linear.forward(
            inputs=fh_hadamard_outputs,
            given_inputs_QParams=self.fh_hadamard.outputs_QParams,
        )
        ni_linear_outputs = self.ni_linear.forward(
            inputs=inputs,
            given_inputs_QParams=self.inputs_QParams,
        )
        n_addition_outputs = self.n_addition.forward(
            inputs1=ni_linear_outputs,
            inputs2=fh_linear_outputs,
            given_inputs1_QParams=self.ni_linear.outputs_QParams,
            given_inputs2_QParams=self.fh_linear.outputs_QParams,
        )
        n_tanh_outputs = self.n_tanh.forward(
            inputs=n_addition_outputs,
            given_inputs_QParams=self.n_addition.outputs_QParams
        )

        #self.h_prev_QParams.update_quant_params(torch.tensor(3.0, dtype=torch.float32))
        #self.h_prev_QParams.update_quant_params(torch.tensor(-3.0, dtype=torch.float32))
        one_minus_f_outputs = self.one_minus_f.forward(
            inputs1=torch.tensor(1),
            inputs2=f_sigmoid_outputs,
            given_inputs1_QParams=self.f_sigmoid.outputs_QParams,
            given_inputs2_QParams=self.f_sigmoid.outputs_QParams,
        )
        
        fN_hadamard_outputs = self.fN_hadamard.forward(
            inputs1=one_minus_f_outputs,
            inputs2=n_tanh_outputs,
            given_inputs1_QParams=self.one_minus_f.outputs_QParams,
            given_inputs2_QParams=self.n_tanh.outputs_QParams,
        )
        h_next = self.h_next_addition.forward(
            inputs1=fN_hadamard_outputs,
            inputs2=fh_hadamard_outputs,
            given_inputs1_QParams=self.fN_hadamard.outputs_QParams,
            given_inputs2_QParams=self.fh_hadamard.outputs_QParams,
        )

        self.h_next_QParams = self.h_next_addition.outputs_QParams
        c_next = None
        return h_next, c_next
