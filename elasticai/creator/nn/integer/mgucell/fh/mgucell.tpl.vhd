library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ${work_library_name};
use ${work_library_name}.all;
entity ${name} is
    generic(
        DATA_WIDTH : integer := ${data_width};
        CONCATENATE_X_1_ADDR_WIDTH : integer := ${concatenate_x_1_addr_width};
        CONCATENATE_X_2_ADDR_WIDTH : integer := ${concatenate_x_2_addr_width};
        CONCATENATE_Y_ADDR_WIDTH : integer := ${concatenate_y_addr_width};
        F_LINEAR_X_ADDR_WIDTH : integer := ${f_linear_x_addr_width};
        F_LINEAR_Y_ADDR_WIDTH : integer := ${f_linear_y_addr_width};
        FH_HADAMARD_X_ADDR_WIDTH : integer := ${fh_hadamard_x_addr_width};
        FH_HADAMARD_Y_ADDR_WIDTH : integer := ${fh_hadamard_y_addr_width};
        NI_LINEAR_X_ADDR_WIDTH : integer := ${ni_linear_x_addr_width};
        NI_LINEAR_Y_ADDR_WIDTH : integer := ${ni_linear_y_addr_width};
        FH_LINEAR_X_ADDR_WIDTH : integer := ${fh_linear_x_addr_width};
        FH_LINEAR_Y_ADDR_WIDTH : integer := ${fh_linear_y_addr_width};
        FN_HADAMARD_X_ADDR_WIDTH : integer := ${fn_hadamard_x_addr_width};
        FN_HADAMARD_Y_ADDR_WIDTH : integer := ${fn_hadamard_y_addr_width};
        ONE_MINUS_f_HYPER_PARAMETER_ONE: integer := ${one_minus_f_hyper_parameter_one};
        ONE_MINUS_f_X_ADDR_WIDTH : integer := ${one_minus_f_x_addr_width};
        ONE_MINUS_f_Y_ADDR_WIDTH : integer := ${one_minus_f_y_addr_width};
        N_ADDITION_X_ADDR_WIDTH : integer := ${n_addition_x_addr_width};
        N_ADDITION_Y_ADDR_WIDTH : integer := ${n_addition_y_addr_width};
        H_NEXT_ADDITION_X_ADDR_WIDTH : integer := ${h_next_addition_x_addr_width};
        H_NEXT_ADDITION_Y_ADDR_WIDTH : integer := ${h_next_addition_y_addr_width}
        );
    port(
        enable: in std_logic;
        clock : in std_logic;
        x_1_address : out std_logic_vector(CONCATENATE_X_1_ADDR_WIDTH -1 downto 0);
        x_2_address : out std_logic_vector(CONCATENATE_X_2_ADDR_WIDTH -1 downto 0);
        x_1 : in std_logic_vector(DATA_WIDTH -1 downto 0);
        x_2 : in std_logic_vector(DATA_WIDTH -1 downto 0);
        y_address : in std_logic_vector(H_NEXT_ADDITION_Y_ADDR_WIDTH -1 downto 0);
        y : out std_logic_vector(DATA_WIDTH -1 downto 0);
        done : out std_logic
        );
    end ${name};
architecture rtl of ${name} is
    function log2(val : INTEGER) return natural is
        variable result : natural;
    begin
        for i in 1 to 31 loop
            if (val <= (2 ** i)) then
                result := i;
                exit;
            end if;
        end loop;
        return result;
    end function log2;
    
    signal concatenate_enable : std_logic;
    signal concatenate_clock  : std_logic;
    signal concatenate_x_1_address : std_logic_vector(CONCATENATE_X_1_ADDR_WIDTH -1 downto 0);
    signal concatenate_x_2_address : std_logic_vector(CONCATENATE_X_2_ADDR_WIDTH -1 downto 0);
    signal concatenate_x_1 : std_logic_vector(DATA_WIDTH -1 downto 0);
    signal concatenate_x_2 : std_logic_vector(DATA_WIDTH -1 downto 0);
    signal concatenate_y_address : std_logic_vector(CONCATENATE_Y_ADDR_WIDTH -1 downto 0);
    signal concatenate_y : std_logic_vector(DATA_WIDTH -1 downto 0);
    signal concatenate_done : std_logic;

    signal f_gate_linear_enable : std_logic;
    signal f_gate_linear_clock : std_logic;
    signal f_gate_linear_x_address : std_logic_vector(F_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal f_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f_gate_linear_y_address : std_logic_vector(F_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal f_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f_gate_linear_done : std_logic;

    signal ni_gate_linear_enable : std_logic;
    signal ni_gate_linear_clock : std_logic;
    signal ni_gate_linear_x_address : std_logic_vector(NI_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal ni_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal ni_gate_linear_y_address : std_logic_vector(NI_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal ni_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal ni_gate_linear_done : std_logic;

    signal fh_gate_linear_enable : std_logic;
    signal fh_gate_linear_clock : std_logic;
    signal fh_gate_linear_x_address : std_logic_vector(FH_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal fh_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fh_gate_linear_y_address : std_logic_vector(FH_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal fh_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fh_gate_linear_done : std_logic;

    signal n_addition_enable : std_logic;
    signal n_addition_clock : std_logic;
    signal n_addition_x_1_address : std_logic_vector(NI_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal n_addition_x_2_address : std_logic_vector(FH_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal n_addition_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_y_address : std_logic_vector(NI_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal n_addition_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_done : std_logic;
    
    signal fh_hadamard_product_enable : std_logic;
    signal fh_hadamard_product_clock : std_logic;
    signal fh_hadamard_product_x_1_address : std_logic_vector(FH_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal fh_hadamard_product_x_2_address : std_logic_vector(FH_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal fh_hadamard_product_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fh_hadamard_product_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fh_hadamard_product_y_address : std_logic_vector(FH_HADAMARD_Y_ADDR_WIDTH - 1 downto 0);
    signal fh_hadamard_product_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fh_hadamard_product_done : std_logic;

    signal fn_hadamard_product_enable : std_logic;
    signal fn_hadamard_product_clock : std_logic;
    signal fn_hadamard_product_x_1_address : std_logic_vector(FN_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal fn_hadamard_product_x_2_address : std_logic_vector(FN_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal fn_hadamard_product_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fn_hadamard_product_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fn_hadamard_product_y_address : std_logic_vector(FN_HADAMARD_Y_ADDR_WIDTH - 1 downto 0);
    signal fn_hadamard_product_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal fn_hadamard_product_done : std_logic;

    signal f1_subtraction_enable : std_logic;
    signal f1_subtraction_clock : std_logic;
    signal f1_subtraction_x_1_address : std_logic_vector(ONE_MINUS_F_X_ADDR_WIDTH - 1 downto 0);
    signal f1_subtraction_x_2_address : std_logic_vector(ONE_MINUS_F_X_ADDR_WIDTH - 1 downto 0);
    signal f1_subtraction_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f1_subtraction_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f1_subtraction_y_address : std_logic_vector(ONE_MINUS_F_Y_ADDR_WIDTH - 1 downto 0);
    signal f1_subtraction_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f1_subtraction_done : std_logic;
    
    signal h_addition_enable : std_logic;
    signal h_addition_clock : std_logic;
    signal h_addition_x_1_address : std_logic_vector(H_NEXT_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal h_addition_x_2_address : std_logic_vector(H_NEXT_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal h_addition_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_y_address : std_logic_vector(H_NEXT_ADDITION_Y_ADDR_WIDTH - 1 downto 0);
    signal h_addition_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_done : std_logic;

    signal f_sigmoid_enable : std_logic;
    signal f_sigmoid_clock : std_logic;
    signal f_sigmoid_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal f_sigmoid_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    
    signal n_tanh_enable : std_logic;
    signal n_tanh_clock : std_logic;
    signal n_tanh_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_tanh_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_tanh_done : std_logic;

    signal temp_x_2_address : std_logic_vector(CONCATENATE_X_2_ADDR_WIDTH -1 downto 0);
    signal temp_f_address : std_logic_vector(F_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
       
    begin

       ---Logic for switching the x_1 and x_2 address
       with concatenate_done select x_1_address <= 
       concatenate_x_1_address when '0',
       ni_gate_linear_x_address when others;


       with concatenate_done select x_2_address <= 
       concatenate_x_2_address when '0',
       fh_hadamard_product_x_2_address when others;
        
       with fh_hadamard_product_done select f_gate_linear_y_address <=
       fh_hadamard_product_x_1_address when '0',
       f1_subtraction_x_2_address when others;

       with fh_gate_linear_done select fh_hadamard_product_y_address <=
       fh_gate_linear_x_address when '0',
       h_addition_x_2_address when others;
       ----------------------------------------------
        concatenate_enable <= enable;
       concatenate_clock <= clock;
       concatenate_x_1 <= x_1;
       concatenate_x_2 <= x_2;
       inst_${name}_concatenate: entity ${work_library_name}.${name}_concatenate(rtl)
        port map (
            enable => concatenate_enable,
            clock  => concatenate_clock,
            x_1_address  => concatenate_x_1_address,
            x_2_address  => concatenate_x_2_address,
            y_address  => concatenate_y_address,
            x_1  => concatenate_x_1,
            x_2  => concatenate_x_2,
            y => concatenate_y,
            done  => concatenate_done
        );
        concatenate_y_address <= f_gate_linear_x_address;
            
        f_gate_linear_enable <= concatenate_done;
        f_gate_linear_clock <= clock;
        f_gate_linear_x <= concatenate_y;
        inst_${name}_f_linear: entity ${work_library_name}.${name}_f_linear(rtl)
        port map (
            enable => f_gate_linear_enable,
            clock  => f_gate_linear_clock,
            x_address  => f_gate_linear_x_address,
            y_address  => f_gate_linear_y_address,
            x  => f_gate_linear_x,
            y => f_gate_linear_y,
            done  => f_gate_linear_done
        );        

        f_sigmoid_enable <= f_gate_linear_done;
        f_sigmoid_x <= f_gate_linear_y;
        f_sigmoid_clock <= clock;
        inst_${name}_f_sigmoid: entity ${work_library_name}.${name}_f_sigmoid(rtl)
        port map(
            enable => f_sigmoid_enable,
            clock => f_sigmoid_clock,
            x => f_sigmoid_x,
            y => f_sigmoid_y
        );
        
        fh_hadamard_product_enable <= f_gate_linear_done;
        fh_hadamard_product_clock <= clock;
        fh_hadamard_product_x_1 <= f_sigmoid_y;
        fh_hadamard_product_x_2 <= x_2;
        inst_${name}_fh_hadamard: entity ${work_library_name}.${name}_fh_hadamard(rtl)
        port map (
            enable => fh_hadamard_product_enable,
            clock  => fh_hadamard_product_clock,
            x_1_address  => fh_hadamard_product_x_1_address,
            x_2_address  => fh_hadamard_product_x_2_address,
            y_address  => fh_hadamard_product_y_address,
            x_1  => fh_hadamard_product_x_1,
            x_2  => fh_hadamard_product_x_2,
            y => fh_hadamard_product_y,
            done  => fh_hadamard_product_done
        );

        ni_gate_linear_enable <= concatenate_done;
        ni_gate_linear_clock <= clock;
        ni_gate_linear_x <= x_1;
        inst_${name}_ni_gate_linear: entity ${work_library_name}.${name}_ni_linear(rtl)
        port map (
            enable => ni_gate_linear_enable,
            clock  => ni_gate_linear_clock,
            x_address  => ni_gate_linear_x_address,
            y_address  => ni_gate_linear_y_address,
            x  => ni_gate_linear_x,
            y => ni_gate_linear_y,
            done  => ni_gate_linear_done
        );
        fh_gate_linear_enable <= fh_hadamard_product_done;
        fh_gate_linear_clock <= clock;
        fh_gate_linear_x <= fh_hadamard_product_y;
        inst_${name}_fh_gate_linear: entity ${work_library_name}.${name}_fh_linear(rtl)
        port map (
            enable => fh_gate_linear_enable,
            clock  => fh_gate_linear_clock,
            x_address  => fh_gate_linear_x_address,
            y_address  => fh_gate_linear_y_address,
            x  => fh_gate_linear_x,
            y => fh_gate_linear_y,
            done  => fh_gate_linear_done
        );
        n_addition_enable <= ni_gate_linear_done and fh_gate_linear_done;
        n_addition_clock <= clock;
        ni_gate_linear_y_address <= n_addition_x_1_address;
        fh_gate_linear_y_address <= n_addition_x_2_address;
        n_addition_x_1 <= ni_gate_linear_y;
        n_addition_x_2 <= fh_gate_linear_y;
        inst_${name}_n_addition : entity ${work_library_name}.${name}_n_addition(rtl)
        port map(
            enable => n_addition_enable,
            clock => n_addition_clock,
            x_1_address=> n_addition_x_1_address,
            x_2_address => n_addition_x_2_address,
            y_address => n_addition_y_address,
            x_1 => n_addition_x_1,
            x_2 => n_addition_x_2,
            y => n_addition_y,
            done => n_addition_done
        );
        n_tanh_enable <= n_addition_done;
        n_tanh_clock <= clock;
        n_tanh_x <= n_addition_y;
        inst_${name}_n_tanh : entity ${work_library_name}.${name}_n_tanh(rtl)
        port map(
            enable => n_tanh_enable,
            clock => n_tanh_clock,
            x => n_tanh_x,
            y => n_tanh_y
        );

        f1_subtraction_enable <= f_gate_linear_done;
        f1_subtraction_clock <= clock;
        f1_subtraction_x_1 <= std_logic_vector(to_signed(ONE_MINUS_F_HYPER_PARAMETER_ONE, DATA_WIDTH));
        f1_subtraction_x_2 <= f_sigmoid_y;
        inst_${name}_one_minus_f : entity ${work_library_name}.${name}_one_minus_f(rtl)
        port map(
            enable => f1_subtraction_enable,
            clock => f1_subtraction_clock,
            x_1_address=> f1_subtraction_x_1_address,
            x_2_address => f1_subtraction_x_2_address,
            y_address => f1_subtraction_y_address,
            x_1 => f1_subtraction_x_1,
            x_2 => f1_subtraction_x_2,
            y => f1_subtraction_y,
            done => f1_subtraction_done
        );

        fn_hadamard_product_enable <= f1_subtraction_done and n_addition_done;
        fn_hadamard_product_clock <= clock;
        f1_subtraction_y_address <= fn_hadamard_product_x_1_address;
        n_addition_y_address <= fn_hadamard_product_x_2_address;
        fn_hadamard_product_x_1 <= f1_subtraction_y;
        fn_hadamard_product_x_2 <= n_tanh_y;
        inst_${name}_fn_hadamard: entity ${work_library_name}.${name}_fn_hadamard(rtl)
        port map (
            enable => fn_hadamard_product_enable,
            clock  => fn_hadamard_product_clock,
            x_1_address  => fn_hadamard_product_x_1_address,
            x_2_address  => fn_hadamard_product_x_2_address,
            y_address  => fn_hadamard_product_y_address,
            x_1  => fn_hadamard_product_x_1,
            x_2  => fn_hadamard_product_x_2,
            y => fn_hadamard_product_y,
            done  => fn_hadamard_product_done
        );

        h_addition_enable <= fh_hadamard_product_done and fn_hadamard_product_done;
        h_addition_clock <= clock;
        fn_hadamard_product_y_address <= h_addition_x_1_address;

        h_addition_x_1 <= fn_hadamard_product_y;
        h_addition_x_2 <= fh_hadamard_product_y;
        inst_${name}_h_next_addition : entity ${work_library_name}.${name}_h_next_addition(rtl)
        port map(
            enable => h_addition_enable,
            clock => h_addition_clock,
            x_1_address=>h_addition_x_1_address,
            x_2_address => h_addition_x_2_address,
            y_address => h_addition_y_address,
            x_1 => h_addition_x_1,
            x_2 => h_addition_x_2,
            y => h_addition_y,
            done => h_addition_done
        );
        y <= h_addition_y;
        h_addition_y_address <= y_address;
        done <= h_addition_done;
end architecture;