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
        z_linear: object,
        z_sigmoid: object,
        r_linear: object,
        r_sigmoid: object,
        ni_linear: object,
        nh_linear: object,
        rnh_hadamard: object,
        n_addition : object,
        n_tanh : object,
        one_minus_z: object,
        zH_hadamard: object,
        zN_hadamard : object,
        h_next_addition: object,
        quantized_one: object,
        work_library_name: str,
    ):
        super().__init__(name=name)

        self._data_width = data_width
        self._work_library_name = work_library_name
        self._r_linear = r_linear #
        self._z_linear = z_linear #
        self._r_sigmoid = r_sigmoid #
        self._z_sigmoid = z_sigmoid #
        self._ni_linear = ni_linear#
        self._nh_linear = nh_linear#
        self._rnh_hadamard = rnh_hadamard#
        self._n_addition = n_addition#
        self._n_tanh = n_tanh #
        self._one_minus_z = one_minus_z#
        self._zH_hadamard = zH_hadamard#
        self._zN_hadamard = zN_hadamard#
        self._h_next_addition = h_next_addition#
        self._quantized_one = quantized_one


        #Linear 4
        self.r_linear_design = self._r_linear.create_design(
            name=self._r_linear.name
        )
        self.z_linear_design = self._z_linear.create_design(
            name=self._z_linear.name
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
        self.one_minus_z_design = self._one_minus_z.create_design(
            name=self._one_minus_z.name
        )
        self.h_next_addition_design = self._h_next_addition.create_design(
            name=self._h_next_addition.name
        )

        #Hadamard Products 3
        self.rnh_hadamard_design = self._rnh_hadamard.create_design(
            name=self._rnh_hadamard.name
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
            x_count=self.ni_linear_design._x_count,
            y_count=self.h_next_addition_design._y_count,
        )

    def save_to(self, destination: Path) -> None:
        #Linears 4
        self.z_linear_design.save_to(destination.create_subpath(self._z_linear.name))
        self.r_linear_design.save_to(destination.create_subpath(self._r_linear.name))
        self.ni_linear_design.save_to(destination.create_subpath(self._ni_linear.name))
        self.nh_linear_design.save_to(destination.create_subpath(self._nh_linear.name))
        #Activation Functions 3
        self.r_sigmoid_design.save_to(destination.create_subpath(self._r_sigmoid.name))
        self.z_sigmoid_design.save_to(destination.create_subpath(self._z_sigmoid.name))
        self.n_tanh_design.save_to(destination.create_subpath(self._n_tanh.name))
        #Additions 3
        self.n_addition_design.save_to(destination.create_subpath(self._n_addition.name))
        self.one_minus_z_design.save_to(destination.create_subpath(self._one_minus_z.name))
        self.h_next_addition_design.save_to(destination.create_subpath(self._h_next_addition.name))
        #Hadamard Products 3
        self.rnh_hadamard_design.save_to(destination.create_subpath(self._rnh_hadamard.name))
        self.zH_hadamard_design.save_to(destination.create_subpath(self._zH_hadamard.name))
        self.zN_hadamard_design.save_to(destination.create_subpath(self._zN_hadamard.name))

        template = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="grucell_1.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                #Linears
                r_linear_x_addr_width=str(self.r_linear_design._x_addr_width),
                r_linear_y_addr_width=str(self.r_linear_design._y_addr_width),
                z_linear_x_addr_width=str(self.z_linear_design._x_addr_width),
                z_linear_y_addr_width=str(self.z_linear_design._y_addr_width),
                ni_linear_x_addr_width=str(self.ni_linear_design._x_addr_width),
                ni_linear_y_addr_width=str(self.ni_linear_design._y_addr_width),
                nh_linear_x_addr_width=str(self.nh_linear_design._x_addr_width),
                nh_linear_y_addr_width=str(self.nh_linear_design._y_addr_width),
                #Hadamard
                rnh_hadamard_x_addr_width=str(self.rnh_hadamard_design._x_addr_width),
                rnh_hadamard_y_addr_width=str(self.rnh_hadamard_design._y_addr_width),
                zn_hadamard_x_addr_width=str(self.zN_hadamard_design._x_addr_width),
                zn_hadamard_y_addr_width=str(self.zN_hadamard_design._y_addr_width),
                zh_hadamard_x_addr_width=str(self.zH_hadamard_design._x_addr_width),
                zh_hadamard_y_addr_width=str(self.zH_hadamard_design._y_addr_width),
                #Addition
                n_addition_x_addr_width = str(self.n_addition_design._x_addr_width),
                n_addition_y_addr_width = str(self.n_addition_design._y_addr_width),
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
               x_1_addr_width=str(self.ni_linear_design._x_addr_width),
               x_2_addr_width=str(self.nh_linear_design._x_addr_width),
               y_1_addr_width=str(self.h_next_addition_design._y_addr_width),
               x_1_num_features=str(self.ni_linear_design._x_count),
               x_1_num_dimensions=str(self.ni_linear_design._num_dimensions),
               x_2_num_features=str(self.nh_linear_design._x_count),
               x_2_num_dimensions=str(self.nh_linear_design._num_dimensions),
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
