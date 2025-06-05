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
        rhprev_hadamard_product: object,
        irhprev_concatenate: object,
        h_tilde_gate_linear: object, 
        h_tanh: object,
        zhprev_hadamard_product: object,
        zhtilde_hadamard_product : object,
        h_next_addition: object,
        work_library_name: str,
    ):
        super().__init__(name=name)

        self._data_width = data_width
        self._work_library_name = work_library_name
        self._ihprev_concatenate = ihprev_concatenate #
        self._r_gate_linear = r_gate_linear #
        self._z_gate_linear = z_gate_linear #
        self._h_tilde_gate_linear = h_tilde_gate_linear #
        self._r_sigmoid = r_sigmoid #
        self._z_sigmoid = z_sigmoid #
        self._h_tanh = h_tanh #
        self._h_next_addition = h_next_addition #
        self._rhprev_hadamard_product = rhprev_hadamard_product #
        self._irhprev_concatenate = irhprev_concatenate #
        self._zhprev_hadamard_product = zhprev_hadamard_product #
        self._zhtilde_hadamard_product = zhtilde_hadamard_product #

        self.ihprev_concatenate_design = self._ihprev_concatenate.create_design(
            name=self._ihprev_concatenate.name
        )
        self.r_gate_linear_design = self._r_gate_linear.create_design(
            name=self._r_gate_linear.name
        )
        self.z_gate_linear_design = self._z_gate_linear.create_design(
            name=self._z_gate_linear.name
        )
        self.h_tilde_gate_linear_design = self._h_tilde_gate_linear.create_design(
            name=self._h_tilde_gate_linear.name
        )
        self.r_sigmoid_design = self._r_sigmoid.create_design(name=self._r_sigmoid.name)
        self.z_sigmoid_design = self._z_sigmoid.create_design(name=self._z_sigmoid.name)
        self.h_tanh_design = self._h_tanh.create_design(name=self._h_tanh.name)
        self.h_next_addition_design = self._h_next_addition.create_design(
            name=self._h_next_addition.name
        )
        self.rhprev_hadamard_product_design = self._rhprev_hadamard_product.create_design(
            name=self._rhprev_hadamard_product.name
        )
        self.zhprev_hadamard_product_design = self._zhprev_hadamard_product.create_design(
            name=self._zhprev_hadamard_product.name
        )
        self.zhtilde_hadamard_product_design = self._zhtilde_hadamard_product.create_design(
            name=self._zhtilde_hadamard_product.name
        )
        self.irhprev_concatenate_design = self._irhprev_concatenate.create_design(
            name=self._irhprev_concatenate.name
        )

    def port(self) -> Port:
        return create_port(
            x_width=self._data_width,
            y_width=self._data_width,
            x_count=self.concatenate_design._x_count,
            y_count=self.oc_hadamard_product_design._y_count,
        )

    def save_to(self, destination: Path) -> None:
        self.ihprev_concatenate_design.save_to(destination)
        self.r_gate_linear_design.save_to(destination)
        self.z_gate_linear_design.save_to(destination)
        self.h_tilde_gate_linear_design.save_to(destination)
        self.r_sigmoid_design.save_to(destination)
        self.z_sigmoid_design.save_to(destination)
        self.h_tanh_design.save_to(destination)
        self.h_next_addition_design.save_to(destination)
        self.rhprev_hadamard_product_design.save_to(destination)
        self.zhprev_hadamard_product_design.save_to(destination)
        self.zhtilde_hadamard_product_design.save_to(destination)
        self.irhprev_concatenate_design.save_to(destination)

        template = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="grucell.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                ihprev_concatenate_x_1_addr_width=str(self.ihprev_concatenate_design._x_1_addr_width),
                ihprev_concatenate_x_2_addr_width=str(self.ihprev_concatenate_design._x_2_addr_width),
                ihprev_concatenate_y_addr_width=str(self.ihprev_concatenate_design._y_addr_width),
                irhprev_concatenate_x_1_addr_width=str(self.irhprev_concatenate_design._x_1_addr_width),
                irhprev_concatenate_x_2_addr_width=str(self.irhprev_concatenate_design._x_2_addr_width),
                irhprev_concatenate_y_addr_width=str(self.irhprev_concatenate_design._y_addr_width),
                r_gate_linear_x_addr_width=str(self.r_gate_linear_design._x_addr_width),
                r_gate_linear_y_addr_width=str(self.r_gate_linear_design._y_addr_width),
                z_gate_linear_x_addr_width=str(self.z_gate_linear_design._x_addr_width),
                z_gate_linear_y_addr_width=str(self.z_gate_linear_design._y_addr_width),
                h_tilde_gate_linear_x_addr_width=str(self.h_tilde_gate_linear_design._x_addr_width),
                h_tilde_gate_linear_y_addr_width=str(self.h_tilde_gate_linear_design._y_addr_width),
                # r_sigmoid_x_addr_width=str(self.r_sigmoid_design._x_addr_width),
                # r_sigmoid_y_addr_width=str(self.r_sigmoid_design._y_addr_width),
                # z_sigmoid_x_addr_width=str(self.z_sigmoid_design._x_addr_width),
                # z_sigmoid_y_addr_width=str(self.z_sigmoid_design._y_addr_width),
                # h_tanh_x_addr_width=str(self.h_tanh_design._x_addr_width),
                # h_tanh_y_addr_width=str(self.h_tanh_design._y_addr_width),
                h_next_addition_x_addr_width=str(
                    self.h_next_addition_design._x_addr_width
                ),
                h_next_addition_y_addr_width=str(
                    self.h_next_addition_design._y_addr_width
                ),
                rhprev_hadamard_product_x_addr_width=str(
                    self.rhprev_hadamard_product_design._x_addr_width
                ),
                rhprev_hadamard_product_y_addr_width=str(
                    self.rhprev_hadamard_product_design._y_addr_width
                ),
                zhtilde_hadamard_product_x_addr_width=str(
                    self.zhtilde_hadamard_product_design._x_addr_width
                ),
                zhtilde_hadamard_product_y_addr_width=str(
                    self.zhtilde_hadamard_product_design._y_addr_width
                ),
                work_library_name=self._work_library_name,
            ),
        )
        destination.create_subpath(self.name).as_file(".vhd").write(template)

        template_test = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="grucell_tb.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                x_1_addr_width=str(self.concatenate_design._x_1_addr_width),
                x_2_addr_width=str(self.concatenate_design._x_2_addr_width),
                x_3_addr_width=str(self.fc_hadamard_product_design._x_1_addr_width),
                y_1_addr_width=str(self.oc_hadamard_product_design._y_addr_width),
                y_2_addr_width=str(self.fc_hadamard_product_design._y_addr_width),
                x1_num_features=str(self.concatenate_design._x1_num_features),
                x1_num_dimensions=str(self.concatenate_design._x1_num_dimensions),
                x2_num_features=str(self.concatenate_design._x2_num_features),
                x2_num_dimensions=str(self.concatenate_design._x2_num_dimensions),
                x_3_num_features=str(self.fc_hadamard_product_design._x_1_num_features),
                x_3_num_dimensions=str(
                    self.fc_hadamard_product_design._x_1_num_dimensions
                ),
                y_1_num_features=str(self.oc_hadamard_product_design._y_num_features),
                y_1_num_dimensions=str(
                    self.oc_hadamard_product_design._y_num_dimensions
                ),
                y_2_num_features=str(self.fc_hadamard_product_design._y_num_features),
                y_2_num_dimensions=str(
                    self.fc_hadamard_product_design._y_num_dimensions
                ),
                work_library_name=self._work_library_name,
            ),
        )
        destination.create_subpath(f"{self.name}_tb").as_file(".vhd").write(
            template_test
        )
