from elasticai.creator.file_generation.savable import Path
from elasticai.creator.file_generation.template import (
    InProjectTemplate,
    module_to_package,
)
from elasticai.creator.vhdl.auto_wire_protocols.port_definitions import create_port
from elasticai.creator.vhdl.design.design import Design
from elasticai.creator.vhdl.design.ports import Port


class MGUCell(Design):
    def __init__(
        self,
        name: str,
        data_width: int,
        concatenate: object,
        f_linear: object,
        f_sigmoid: object,
        fh_hadamard: object,
        fh_linear: object,
        ni_linear: object,
        n_addition: object,
        n_tanh : object,
        one_minus_f: object,
        fN_hadamard : object,
        h_next_addition: object,
        quantized_one: object,
        work_library_name: str,
    ):
        super().__init__(name=name)

        self._data_width = data_width
        self._work_library_name = work_library_name
        self._concatenate = concatenate #
        self._f_linear = f_linear #
        self._f_sigmoid = f_sigmoid #
        self._fh_hadamard = fh_hadamard#
        self._fh_linear = fh_linear#
        self._ni_linear = ni_linear#
        self._n_addition = n_addition#
        self._n_tanh = n_tanh #
        self._one_minus_f = one_minus_f#
        self._fN_hadamard = fN_hadamard#
        self._h_next_addition = h_next_addition#
        self._quantized_one = quantized_one

        self.concatenate_design = self._concatenate.create_design(
            name=self._concatenate.name
        )


        #Linear 4
        self.f_linear_design = self._f_linear.create_design(
            name=self._f_linear.name
        )
        self.ni_linear_design = self._ni_linear.create_design(
            name=self._ni_linear.name
        )
        self.fh_linear_design = self._fh_linear.create_design(
            name=self._fh_linear.name
        )

        #Activation Functions 3
        self.f_sigmoid_design = self._f_sigmoid.create_design(name=self._f_sigmoid.name)
        self.n_tanh_design = self._n_tanh.create_design(name=self._n_tanh.name)

        #Additions 3
        self.one_minus_f_design = self._one_minus_f.create_design(
            name=self._one_minus_f.name
        )
        self.n_addition_design = self._n_addition.create_design(
            name=self._n_addition.name
        )
        self.h_next_addition_design = self._h_next_addition.create_design(
            name=self._h_next_addition.name
        )

        #Hadamard Products 3
        self.fh_hadamard_design = self._fh_hadamard.create_design(
            name=self._fh_hadamard.name
        )
        self.fN_hadamard_design = self._fN_hadamard.create_design(
            name=self._fN_hadamard.name
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
        #Linears 4
        self.f_linear_design.save_to(destination.create_subpath(self._f_linear.name))
        self.ni_linear_design.save_to(destination.create_subpath(self._ni_linear.name))
        self.fh_linear_design.save_to(destination.create_subpath(self._fh_linear.name))
        #Activation Functions 3
        self.f_sigmoid_design.save_to(destination.create_subpath(self._f_sigmoid.name))
        self.n_tanh_design.save_to(destination.create_subpath(self._n_tanh.name))
        #Additions 3
        self.one_minus_f_design.save_to(destination.create_subpath(self._one_minus_f.name))
        self.n_addition_design.save_to(destination.create_subpath(self._n_addition.name))
        self.h_next_addition_design.save_to(destination.create_subpath(self._h_next_addition.name))
        #Hadamard Products 3
        self.fh_hadamard_design.save_to(destination.create_subpath(self._fh_hadamard.name))
        self.fN_hadamard_design.save_to(destination.create_subpath(self._fN_hadamard.name))

        template = InProjectTemplate(
            package=module_to_package(self.__module__),
            file_name="mgucell.tpl.vhd",
            parameters=dict(
                name=self.name,
                data_width=str(self._data_width),
                concatenate_x_1_addr_width=str(self.concatenate_design._x_1_addr_width),
                concatenate_x_2_addr_width=str(self.concatenate_design._x_2_addr_width),
                concatenate_y_addr_width=str(self.concatenate_design._y_addr_width),
                #Linears
                f_linear_x_addr_width=str(self.f_linear_design._x_addr_width),
                f_linear_y_addr_width=str(self.f_linear_design._y_addr_width),
                ni_linear_x_addr_width=str(self.ni_linear_design._x_addr_width),
                ni_linear_y_addr_width=str(self.ni_linear_design._y_addr_width),
                fh_linear_x_addr_width=str(self.fh_linear_design._x_addr_width),
                fh_linear_y_addr_width=str(self.fh_linear_design._y_addr_width),
                #Hadamard
                fh_hadamard_x_addr_width=str(self.fh_hadamard_design._x_addr_width),
                fh_hadamard_y_addr_width=str(self.fh_hadamard_design._y_addr_width),
                fn_hadamard_x_addr_width=str(self.fN_hadamard_design._x_addr_width),
                fn_hadamard_y_addr_width=str(self.fN_hadamard_design._y_addr_width),
                #Addition
                one_minus_f_hyper_parameter_one = str(self._quantized_one),
                one_minus_f_x_addr_width=str(self.one_minus_f_design._x_addr_width),
                one_minus_f_y_addr_width=str(self.one_minus_f_design._y_addr_width),
                n_addition_x_addr_width=str(self.n_addition_design._x_addr_width),
                n_addition_y_addr_width=str(self.n_addition_design._y_addr_width),
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
           file_name="mgucell_tb.tpl.vhd",
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
