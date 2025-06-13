from elasticai.creator.file_generation.savable import Path
from elasticai.creator.file_generation.template import (
    InProjectTemplate,
    module_to_package,
)
from elasticai.creator.vhdl.auto_wire_protocols.port_definitions import create_port
from elasticai.creator.vhdl.design.design import Design
from elasticai.creator.vhdl.design.ports import Port


class GRUCell(Design):
    def __init__(
        self,
        name: str,
        data_width: int,
        ihprev_concatenate: object,
        z_gate_linear: object,
        z_sigmoid: object,
        r_gate_linear: object,
        r_sigmoid: object,
        ni_linear: object,
        nh_linear: object,
        rnh_hadamard: object,
        n_addition : object,
        n_tanh : object,
        minus_z_addition: object,
        zhprev_hadamard_product: object,
        zn_hadamard_product : object,
        h_next_addition: object,
        quantized_one: object,
        work_library_name: str,
    ):
        super().__init__(name=name)

        self._data_width = data_width
        self._work_library_name = work_library_name
        self._ihprev_concatenate = ihprev_concatenate #
        self._r_gate_linear = r_gate_linear #
        self._z_gate_linear = z_gate_linear #
        self._r_sigmoid = r_sigmoid #
        self._z_sigmoid = z_sigmoid #
        self._ni_linear = ni_linear#
        self._nh_linear = nh_linear#
        self._rnh_hadamard_product = rnh_hadamard#
        self._n_addition = n_addition#
        self._n_tanh = n_tanh #
        self._minus_z_addition = minus_z_addition#
        self._zhprev_hadamard_product = zhprev_hadamard_product#
        self._zn_hadamard_product = zn_hadamard_product#
        self._h_next_addition = h_next_addition#
        self._quantized_one = quantized_one

        self.ihprev_concatenate_design = self._ihprev_concatenate.create_design(
            name=self._ihprev_concatenate.name
        )

        #Linear 4
        self.r_gate_linear_design = self._r_gate_linear.create_design(
            name=self._r_gate_linear.name
        )
        self.z_gate_linear_design = self._z_gate_linear.create_design(
            name=self._z_gate_linear.name
        )
        self.ni_linear_design = self._ni_linear.create_design(
            name=self._ni_linear.name
        )
        self.nh_linear_design = self._nh_linear.create_design(
            name=self._nh_linear.name
        )

        #Activation Functions 3
        self.r_sigmoid_design = self._r_sigmoid.create_design(name=self._r_sigmoid.name)
        self.z_sigmoid_design = self._z_sigmoid.create_design(name=self._z_sigmoid.name)
        self.n_tanh_design = self._n_tanh.create_design(name=self._n_tanh.name)

        #Additions 3
        self.n_addition_design = self._n_addition.create_design(
            name=self._n_addition.name
        )
        self.minus_z_addition_design = self._minus_z_addition.create_design(
            name=self._minus_z_addition.name
        )
        self.h_next_addition_design = self._h_next_addition.create_design(
            name=self._h_next_addition.name
        )

        #Hadamard Products 3
        self.rnh_hadamard_product_design = self._rnh_hadamard_product.create_design(
            name=self._rnh_hadamard_product.name
        )
        self.zhprev_hadamard_product_design = self._zhprev_hadamard_product.create_design(
            name=self._zhprev_hadamard_product.name
        )
        self.zn_hadamard_product_design = self._zn_hadamard_product.create_design(
            name=self._zn_hadamard_product.name
        )



    def port(self) -> Port:
        return create_port(
            x_width=self._data_width,
            y_width=self._data_width,
            x_count=self.ihprev_concatenate_design._x_count,
            y_count=self.h_next_addition_design._y_count,
        )

    def save_to(self, destination: Path) -> None:
        self.ihprev_concatenate_design.save_to(destination.create_subpath(self._ihprev_concatenate.name))
        #Linears 4
        self.z_gate_linear_design.save_to(destination.create_subpath(self._z_gate_linear.name))
        self.r_gate_linear_design.save_to(destination.create_subpath(self._r_gate_linear.name))
        self.ni_linear_design.save_to(destination.create_subpath(self._ni_linear.name))
        self.nh_linear_design.save_to(destination.create_subpath(self._nh_linear.name))
        #Activation Functions 3
        self.r_sigmoid_design.save_to(destination.create_subpath(self._r_sigmoid.name))
        self.z_sigmoid_design.save_to(destination.create_subpath(self._z_sigmoid.name))
        self.n_tanh_design.save_to(destination.create_subpath(self._n_tanh.name))
        #Additions 3
        self.n_addition_design.save_to(destination.create_subpath(self._n_addition.name))
        self.minus_z_addition_design.save_to(destination.create_subpath(self._minus_z_addition.name))
        self.h_next_addition_design.save_to(destination.create_subpath(self._h_next_addition.name))
        #Hadamard Products 3
        self.rnh_hadamard_product_design.save_to(destination.create_subpath(self._rnh_hadamard_product.name))
        self.zhprev_hadamard_product_design.save_to(destination.create_subpath(self._zhprev_hadamard_product.name))
        self.zn_hadamard_product_design.save_to(destination.create_subpath(self._zn_hadamard_product.name))

        template = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="grucell.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                concatenate_x_1_addr_width=str(self.ihprev_concatenate_design._x_1_addr_width),
                concatenate_x_2_addr_width=str(self.ihprev_concatenate_design._x_2_addr_width),
                concatenate_y_addr_width=str(self.ihprev_concatenate_design._y_addr_width),
                #Linears
                r_gate_linear_x_addr_width=str(self.r_gate_linear_design._x_addr_width),
                r_gate_linear_y_addr_width=str(self.r_gate_linear_design._y_addr_width),
                z_gate_linear_x_addr_width=str(self.z_gate_linear_design._x_addr_width),
                z_gate_linear_y_addr_width=str(self.z_gate_linear_design._y_addr_width),
                ni_gate_linear_x_addr_width=str(self.ni_linear_design._x_addr_width),
                ni_gate_linear_y_addr_width=str(self.ni_linear_design._y_addr_width),
                nh_gate_linear_x_addr_width=str(self.nh_linear_design._x_addr_width),
                nh_gate_linear_y_addr_width=str(self.nh_linear_design._y_addr_width),
                #Hadamard
                rnh_hadamard_product_x_addr_width=str(self.rnh_hadamard_product_design._x_addr_width),
                rnh_hadamard_product_y_addr_width=str(self.rnh_hadamard_product_design._y_addr_width),
                zn_hadamard_product_x_addr_width=str(self.zn_hadamard_product_design._x_addr_width),
                zn_hadamard_product_y_addr_width=str(self.zn_hadamard_product_design._y_addr_width),
                zh_hadamard_product_x_addr_width=str(self.zhprev_hadamard_product_design._x_addr_width),
                zh_hadamard_product_y_addr_width=str(self.zhprev_hadamard_product_design._y_addr_width),
                #Addition
                n_addition_x_addr_width = str(self.n_addition_design._x_addr_width),
                n_addition_y_addr_width = str(self.n_addition_design._y_addr_width),
                z1_addition_hyper_parameter_one = str(self._quantized_one),
                z1_addition_x_addr_width=str(self.minus_z_addition_design._x_addr_width),
                z1_addition_y_addr_width=str(self.minus_z_addition_design._y_addr_width),
                h_addition_x_addr_width=str(
                    self.h_next_addition_design._x_addr_width
                ),
                h_addition_y_addr_width=str(
                    self.h_next_addition_design._y_addr_width
                ),
                work_library_name=self._work_library_name,
            ),
        )
        destination.create_subpath(self.name).as_file(".vhd").write(template)

#        template_test = InProjectTemplate(
#           package=module_to_package(self.__module__),
#           file_name="grucell_tb.tpl.vhd",
#           parameters=dict(
#               name=self.name,
#               data_width=str(self._data_width),
#               x_1_addr_width=str(self.ihprev_concatenate_design._x_1_addr_width),
#               x_2_addr_width=str(self.ihprev_concatenate_design._x_2_addr_width),
#               x_3_addr_width=str(self.fc_hadamard_product_design._x_1_addr_width),
#               y_1_addr_width=str(self.oc_hadamard_product_design._y_addr_width),
#               y_2_addr_width=str(self.fc_hadamard_product_design._y_addr_width),
#               x1_num_features=str(self.concatenate_design._x1_num_features),
#               x1_num_dimensions=str(self.concatenate_design._x1_num_dimensions),
#               x2_num_features=str(self.concatenate_design._x2_num_features),
#               x2_num_dimensions=str(self.concatenate_design._x2_num_dimensions),
#               x_3_num_features=str(self.fc_hadamard_product_design._x_1_num_features),
#               x_3_num_dimensions=str(
#                   self.fc_hadamard_product_design._x_1_num_dimensions
#               ),
#               y_1_num_features=str(self.oc_hadamard_product_design._y_num_features),
#               y_1_num_dimensions=str(
#                   self.oc_hadamard_product_design._y_num_dimensions
#               ),
#               y_2_num_features=str(self.fc_hadamard_product_design._y_num_features),
#               y_2_num_dimensions=str(
#                   self.fc_hadamard_product_design._y_num_dimensions
#               ),
#               work_library_name=self._work_library_name,
#           ),
#       )
#       destination.create_subpath(f"{self.name}_tb").as_file(".vhd").write(
#           template_test
#       )
