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
        concatenate: object,
        f_linear: object,
        f_sigmoid: object,
        r_linear: object,
        r_sigmoid: object,
        fh_hadamard: object,
        concatenate_n: object,
        n_linear: object,
        n_tanh : object,
        one_minus_f: object,
        fH_hadamard: object,
        fN_hadamard : object,
        h_next_addition: object,
        quantized_one: object,
        work_library_name: str,
    ):
        super().__init__(name=name)

        self._data_width = data_width
        self._work_library_name = work_library_name
        self._concatenate = concatenate #
        self._r_linear = r_linear #
        self._z_linear = f_linear #
        self._r_sigmoid = r_sigmoid #
        self._z_sigmoid = f_sigmoid #
        self._rh_hadamard = fh_hadamard#
        self._concatenate_n = concatenate_n#
        self._n_linear = n_linear#
        self._n_tanh = n_tanh #
        self._one_minus_z = one_minus_f#
        self._zH_hadamard = fH_hadamard#
        self._zN_hadamard = fN_hadamard#
        self._h_next_addition = h_next_addition#
        self._quantized_one = quantized_one

        self.concatenate_design = self._concatenate.create_design(
            name=self._concatenate.name
        )

        self.concatenate_n_design = self._concatenate_n.create_design(
            name=self._concatenate_n.name
        )
        #Linear 4
        self.r_linear_design = self._r_linear.create_design(
            name=self._r_linear.name
        )
        self.z_linear_design = self._z_linear.create_design(
            name=self._z_linear.name
        )
        self.n_linear_design = self._n_linear.create_design(
            name=self._n_linear.name
        )

        #Activation Functions 3
        self.r_sigmoid_design = self._r_sigmoid.create_design(name=self._r_sigmoid.name)
        self.z_sigmoid_design = self._z_sigmoid.create_design(name=self._z_sigmoid.name)
        self.n_tanh_design = self._n_tanh.create_design(name=self._n_tanh.name)

        #Additions 3
        self.one_minus_z_design = self._one_minus_z.create_design(
            name=self._one_minus_z.name
        )
        self.h_next_addition_design = self._h_next_addition.create_design(
            name=self._h_next_addition.name
        )

        #Hadamard Products 3
        self.rh_hadamard_design = self._rh_hadamard.create_design(
            name=self._rh_hadamard.name
        )
        self.zH_hadamard_design = self._zH_hadamard.create_design(
            name=self._zH_hadamard.name
        )
        self.zN_hadamard_design = self._zN_hadamard.create_design(
            name=self._zN_hadamard.name
        )



    def port(self) -> Port:
        return create_port(
            x_width=self._data_width,
            y_width=self._data_width,
            x_count=self.concatenate_design._x_count,
            y_count=self.h_next_addition_design._y_count,
        )

    def save_to(self, destination: Path) -> None:
        self.concatenate_design.save_to(destination.create_subpath(self._concatenate.name))
        self.concatenate_n_design.save_to(destination.create_subpath(self._concatenate_n.name))
        #Linears 4
        self.z_linear_design.save_to(destination.create_subpath(self._z_linear.name))
        self.r_linear_design.save_to(destination.create_subpath(self._r_linear.name))
        self.n_linear_design.save_to(destination.create_subpath(self._n_linear.name))
        #Activation Functions 3
        self.r_sigmoid_design.save_to(destination.create_subpath(self._r_sigmoid.name))
        self.z_sigmoid_design.save_to(destination.create_subpath(self._z_sigmoid.name))
        self.n_tanh_design.save_to(destination.create_subpath(self._n_tanh.name))
        #Additions 3
        self.one_minus_z_design.save_to(destination.create_subpath(self._one_minus_z.name))
        self.h_next_addition_design.save_to(destination.create_subpath(self._h_next_addition.name))
        #Hadamard Products 3
        self.rh_hadamard_design.save_to(destination.create_subpath(self._rh_hadamard.name))
        self.zH_hadamard_design.save_to(destination.create_subpath(self._zH_hadamard.name))
        self.zN_hadamard_design.save_to(destination.create_subpath(self._zN_hadamard.name))

        template = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="grucell_rh.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                concatenate_x_1_addr_width=str(self.concatenate_design._x_1_addr_width),
                concatenate_x_2_addr_width=str(self.concatenate_design._x_2_addr_width),
                concatenate_y_addr_width=str(self.concatenate_design._y_addr_width),
                #Linears
                r_linear_x_addr_width=str(self.r_linear_design._x_addr_width),
                r_linear_y_addr_width=str(self.r_linear_design._y_addr_width),
                z_linear_x_addr_width=str(self.z_linear_design._x_addr_width),
                z_linear_y_addr_width=str(self.z_linear_design._y_addr_width),
                n_linear_x_addr_width=str(self.n_linear_design._x_addr_width),
                n_linear_y_addr_width=str(self.n_linear_design._y_addr_width),
                #Hadamard
                rh_hadamard_x_addr_width=str(self.rh_hadamard_design._x_addr_width),
                rh_hadamard_y_addr_width=str(self.rh_hadamard_design._y_addr_width),
                zn_hadamard_x_addr_width=str(self.zN_hadamard_design._x_addr_width),
                zn_hadamard_y_addr_width=str(self.zN_hadamard_design._y_addr_width),
                zh_hadamard_x_addr_width=str(self.zH_hadamard_design._x_addr_width),
                zh_hadamard_y_addr_width=str(self.zH_hadamard_design._y_addr_width),
                #Addition
                one_minus_z_hyper_parameter_one = str(self._quantized_one),
                one_minus_z_x_addr_width=str(self.one_minus_z_design._x_addr_width),
                one_minus_z_y_addr_width=str(self.one_minus_z_design._y_addr_width),
                h_next_addition_x_addr_width=str(
                    self.h_next_addition_design._x_addr_width
                ),
                h_next_addition_y_addr_width=str(
                    self.h_next_addition_design._y_addr_width
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
               y_1_addr_width=str(self.h_next_addition_design._y_addr_width),
               x_1_num_features=str(self.concatenate_design._x_1_count),
               x_1_num_dimensions=str(self.concatenate_design._num_dimensions),
               x_2_num_features=str(self.concatenate_design._x_2_count),
               x_2_num_dimensions=str(self.concatenate_design._num_dimensions),
               y_1_num_features=str(self.h_next_addition_design._num_features),
               y_1_num_dimensions=str(
                   self.h_next_addition_design._num_dimensions
               ),
               work_library_name=self._work_library_name,
           ),
       )
        destination.create_subpath(f"{self.name}_tb").as_file(".vhd").write(
           template_test
       )
