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
        R_LINEAR_X_ADDR_WIDTH : integer := ${r_linear_x_addr_width};
        R_LINEAR_Y_ADDR_WIDTH : integer := ${r_linear_y_addr_width};
        Z_LINEAR_X_ADDR_WIDTH : integer := ${z_linear_x_addr_width};
        Z_LINEAR_Y_ADDR_WIDTH : integer := ${z_linear_y_addr_width};
        NI_LINEAR_X_ADDR_WIDTH : integer := ${ni_linear_x_addr_width};
        NI_LINEAR_Y_ADDR_WIDTH : integer := ${ni_linear_y_addr_width};
        NH_LINEAR_X_ADDR_WIDTH : integer := ${nh_linear_x_addr_width};
        NH_LINEAR_Y_ADDR_WIDTH : integer := ${nh_linear_y_addr_width};
        RNH_HADAMARD_X_ADDR_WIDTH : integer := ${rnh_hadamard_x_addr_width};
        RNH_HADAMARD_Y_ADDR_WIDTH : integer := ${rnh_hadamard_y_addr_width};
        ZN_HADAMARD_X_ADDR_WIDTH : integer := ${zn_hadamard_x_addr_width};
        ZN_HADAMARD_Y_ADDR_WIDTH : integer := ${zn_hadamard_y_addr_width};
        ZH_PRODUCT_X_ADDR_WIDTH : integer := ${zh_hadamard_x_addr_width};
        ZH_PRODUCT_Y_ADDR_WIDTH : integer := ${zh_hadamard_y_addr_width};
        N_ADDITION_X_ADDR_WIDTH : integer := ${n_addition_x_addr_width};
        N_ADDITION_Y_ADDR_WIDTH : integer := ${n_addition_y_addr_width};
        ONE_MINUS_Z_HYPER_PARAMETER_ONE: integer := ${one_minus_z_hyper_parameter_one};
        ONE_MINUS_Z_X_ADDR_WIDTH : integer := ${one_minus_z_x_addr_width};
        ONE_MINUS_Z_Y_ADDR_WIDTH : integer := ${one_minus_z_y_addr_width};
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
    
    signal r_gate_linear_enable : std_logic;
    signal r_gate_linear_clock : std_logic;
    signal r_gate_linear_x_address : std_logic_vector(R_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal r_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal r_gate_linear_y_address : std_logic_vector(R_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal r_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal r_gate_linear_done : std_logic;

    signal z_gate_linear_enable : std_logic;
    signal z_gate_linear_clock : std_logic;
    signal z_gate_linear_x_address : std_logic_vector(Z_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal z_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z_gate_linear_y_address : std_logic_vector(Z_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal z_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z_gate_linear_done : std_logic;

    signal ni_gate_linear_enable : std_logic;
    signal ni_gate_linear_clock : std_logic;
    signal ni_gate_linear_x_address : std_logic_vector(NI_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal ni_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal ni_gate_linear_y_address : std_logic_vector(NI_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal ni_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal ni_gate_linear_done : std_logic;

    signal nh_gate_linear_enable : std_logic;
    signal nh_gate_linear_clock : std_logic;
    signal nh_gate_linear_x_address : std_logic_vector(NH_LINEAR_X_ADDR_WIDTH - 1 downto 0);
    signal nh_gate_linear_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal nh_gate_linear_y_address : std_logic_vector(NH_LINEAR_Y_ADDR_WIDTH - 1 downto 0);
    signal nh_gate_linear_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal nh_gate_linear_done : std_logic;
    
    signal rnh_hadamard_product_enable : std_logic;
    signal rnh_hadamard_product_clock : std_logic;
    signal rnh_hadamard_product_x_1_address : std_logic_vector(RNH_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_x_2_address : std_logic_vector(RNH_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_y_address : std_logic_vector(RNH_HADAMARD_Y_ADDR_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal rnh_hadamard_product_done : std_logic;

    signal zn_hadamard_product_enable : std_logic;
    signal zn_hadamard_product_clock : std_logic;
    signal zn_hadamard_product_x_1_address : std_logic_vector(ZN_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal zn_hadamard_product_x_2_address : std_logic_vector(ZN_HADAMARD_X_ADDR_WIDTH - 1 downto 0);
    signal zn_hadamard_product_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zn_hadamard_product_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zn_hadamard_product_y_address : std_logic_vector(ZN_HADAMARD_Y_ADDR_WIDTH - 1 downto 0);
    signal zn_hadamard_product_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zn_hadamard_product_done : std_logic;

    signal zh_hadamard_product_enable : std_logic;
    signal zh_hadamard_product_clock : std_logic;
    signal zh_hadamard_product_x_1_address : std_logic_vector(ZH_PRODUCT_X_ADDR_WIDTH - 1 downto 0);
    signal zh_hadamard_product_x_2_address : std_logic_vector(ZH_PRODUCT_X_ADDR_WIDTH - 1 downto 0);
    signal zh_hadamard_product_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zh_hadamard_product_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zh_hadamard_product_y_address : std_logic_vector(ZH_PRODUCT_Y_ADDR_WIDTH - 1 downto 0);
    signal zh_hadamard_product_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal zh_hadamard_product_done : std_logic;
    
    signal n_addition_enable : std_logic;
    signal n_addition_clock : std_logic;
    signal n_addition_x_1_address : std_logic_vector(N_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal n_addition_x_2_address : std_logic_vector(N_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal n_addition_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_y_address : std_logic_vector(N_ADDITION_Y_ADDR_WIDTH - 1 downto 0);
    signal n_addition_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_addition_done : std_logic;
    
    signal z1_addition_enable : std_logic;
    signal z1_addition_clock : std_logic;
    signal z1_addition_x_1_address : std_logic_vector(ONE_MINUS_Z_X_ADDR_WIDTH - 1 downto 0);
    signal z1_addition_x_2_address : std_logic_vector(ONE_MINUS_Z_X_ADDR_WIDTH - 1 downto 0);
    signal z1_addition_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z1_addition_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z1_addition_y_address : std_logic_vector(ONE_MINUS_Z_Y_ADDR_WIDTH - 1 downto 0);
    signal z1_addition_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z1_addition_done : std_logic;
    
    signal h_addition_enable : std_logic;
    signal h_addition_clock : std_logic;
    signal h_addition_x_1_address : std_logic_vector(H_NEXT_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal h_addition_x_2_address : std_logic_vector(H_NEXT_ADDITION_X_ADDR_WIDTH - 1 downto 0);
    signal h_addition_x_1 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_x_2 : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_y_address : std_logic_vector(H_NEXT_ADDITION_Y_ADDR_WIDTH - 1 downto 0);
    signal h_addition_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal h_addition_done : std_logic;
    
    signal r_sigmoid_enable : std_logic;
    signal r_sigmoid_clock : std_logic;
    signal r_sigmoid_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal r_sigmoid_y: std_logic_vector(DATA_WIDTH - 1 downto 0);

    signal z_sigmoid_enable : std_logic;
    signal z_sigmoid_clock : std_logic;
    signal z_sigmoid_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal z_sigmoid_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    
    signal n_tanh_enable : std_logic;
    signal n_tanh_clock : std_logic;
    signal n_tanh_x : std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_tanh_y: std_logic_vector(DATA_WIDTH - 1 downto 0);
    signal n_tanh_done : std_logic;

    signal temp_x_2_address : std_logic_vector(CONCATENATE_X_2_ADDR_WIDTH -1 downto 0);
    signal temp_z_address : std_logic_vector(Z_LINEAR_Y_ADDR_WIDTH - 1 downto 0);

    signal z_sigmoid_y_integer : integer;
    signal z_sigmoid_y_negative_std : std_logic_vector(DATA_WIDTH - 1 downto 0);
       
    begin
       concatenate_enable <= enable;
       concatenate_clock <= clock;
       ---Logic for switching the x_1 and x_2 address
       with concatenate_done select x_1_address <= 
       concatenate_x_1_address when '0',
       ni_gate_linear_x_address when others;


       with concatenate_done select x_2_address <= 
       concatenate_x_2_address when '0',
       temp_x_2_address when others;

       with nh_gate_linear_done select temp_x_2_address <=
       nh_gate_linear_x_address when '0',
       zh_hadamard_product_x_2_address when others;

       with z1_addition_done select z_gate_linear_y_address <=
       z1_addition_x_1_address when '0',
       temp_z_address when others;

       with zn_hadamard_product_done select temp_z_address <=
         zn_hadamard_product_x_1_address when '0',
         zh_hadamard_product_x_1_address when others;
       ----------------------------------------------
       z_sigmoid_y_integer <= to_integer(signed(z_sigmoid_y)) * (-1);
       z_sigmoid_y_negative_std <= std_logic_vector(to_signed(z_sigmoid_y_integer, DATA_WIDTH));
       
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
        concatenate_y_address <= r_gate_linear_x_address;
        
        r_gate_linear_enable <= concatenate_done;
        r_gate_linear_clock <= clock;
        r_gate_linear_x <= concatenate_y;
        inst_${name}_r_linear: entity ${work_library_name}.${name}_r_linear(rtl)
        port map (
            enable => r_gate_linear_enable,
            clock  => r_gate_linear_clock,
            x_address  => r_gate_linear_x_address,
            y_address  => r_gate_linear_y_address,
            x  => r_gate_linear_x,
            y => r_gate_linear_y,
            done  => r_gate_linear_done
        );
        
        r_sigmoid_enable <= r_gate_linear_done;
        r_sigmoid_x <= r_gate_linear_y;
        r_sigmoid_clock <= clock;
        inst_${name}_r_sigmoid: entity ${work_library_name}.${name}_r_sigmoid(rtl)
        port map(
            enable => r_sigmoid_enable,
            clock => r_sigmoid_clock,
            x => r_sigmoid_x,
            y => r_sigmoid_y
        );
            
        z_gate_linear_enable <= concatenate_done;
        z_gate_linear_clock <= clock;
        z_gate_linear_x <= concatenate_y;
        inst_${name}_z_linear: entity ${work_library_name}.${name}_z_linear(rtl)
        port map (
            enable => z_gate_linear_enable,
            clock  => z_gate_linear_clock,
            x_address  => z_gate_linear_x_address,
            y_address  => z_gate_linear_y_address,
            x  => z_gate_linear_x,
            y => z_gate_linear_y,
            done  => z_gate_linear_done
        );        

        z_sigmoid_enable <= z_gate_linear_done;
        z_sigmoid_x <= z_gate_linear_y;
        z_sigmoid_clock <= clock;
        inst_${name}_z_sigmoid: entity ${work_library_name}.${name}_z_sigmoid(rtl)
        port map(
            enable => z_sigmoid_enable,
            clock => z_sigmoid_clock,
            x => z_sigmoid_x,
            y => z_sigmoid_y
        );
        
        ni_gate_linear_enable <= enable and r_gate_linear_done and z_gate_linear_done;
        ni_gate_linear_clock <= clock;
        ni_gate_linear_x <= x_1;
        inst_${name}_ni_linear: entity ${work_library_name}.${name}_ni_linear(rtl)
        port map (
            enable => ni_gate_linear_enable,
            clock  => ni_gate_linear_clock,
            x_address  => ni_gate_linear_x_address,
            y_address  => ni_gate_linear_y_address,
            x  => ni_gate_linear_x,
            y => ni_gate_linear_y,
            done  => ni_gate_linear_done
        );

        nh_gate_linear_enable <= enable and r_gate_linear_done and z_gate_linear_done;
        nh_gate_linear_clock <= clock;
        nh_gate_linear_x <= x_2;
        inst_${name}_nh_linear: entity ${work_library_name}.${name}_nh_linear(rtl)
        port map (
            enable => nh_gate_linear_enable,
            clock  => nh_gate_linear_clock,
            x_address  => nh_gate_linear_x_address,
            y_address  => nh_gate_linear_y_address,
            x  => nh_gate_linear_x,
            y => nh_gate_linear_y,
            done  => nh_gate_linear_done
        );

        rnh_hadamard_product_enable <= r_gate_linear_done and nh_gate_linear_done;
        rnh_hadamard_product_clock <= clock;
        r_gate_linear_y_address <= rnh_hadamard_product_x_1_address;
        nh_gate_linear_y_address <= rnh_hadamard_product_x_2_address;
        rnh_hadamard_product_x_1 <= r_sigmoid_y;
        rnh_hadamard_product_x_2 <= nh_gate_linear_y;
        inst_${name}_rnh_hadamard: entity ${work_library_name}.${name}_rnh_hadamard(rtl)
        port map (
            enable => rnh_hadamard_product_enable,
            clock  => rnh_hadamard_product_clock,
            x_1_address  => rnh_hadamard_product_x_1_address,
            x_2_address  => rnh_hadamard_product_x_2_address,
            y_address  => rnh_hadamard_product_y_address,
            x_1  => rnh_hadamard_product_x_1,
            x_2  => rnh_hadamard_product_x_2,
            y => rnh_hadamard_product_y,
            done  => rnh_hadamard_product_done
        );

        n_addition_enable <= rnh_hadamard_product_done and ni_gate_linear_done;
        n_addition_clock <= clock;
        ni_gate_linear_y_address <= n_addition_x_1_address;
        rnh_hadamard_product_y_address <= n_addition_x_2_address;
        n_addition_x_1 <= ni_gate_linear_y;
        n_addition_x_2 <= rnh_hadamard_product_y;
        inst_${name}_n_addition : entity ${work_library_name}.${name}_n_addition(rtl)
        port map(
            enable => n_addition_enable,
            clock => n_addition_clock,
            x_1_address=>n_addition_x_1_address,
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

        z1_addition_enable <= z_gate_linear_done and ni_gate_linear_done;
        z1_addition_clock <= clock;
        z1_addition_x_1 <= std_logic_vector(to_signed(ONE_MINUS_Z_HYPER_PARAMETER_ONE, DATA_WIDTH));
        z1_addition_x_2 <= z_sigmoid_y;
        inst_${name}_one_minus_z : entity ${work_library_name}.${name}_one_minus_z(rtl)
        port map(
            enable => z1_addition_enable,
            clock => z1_addition_clock,
            x_1_address=> z1_addition_x_1_address,
            x_2_address => z1_addition_x_2_address,
            y_address => z1_addition_y_address,
            x_1 => z1_addition_x_1,
            x_2 => z1_addition_x_2,
            y => z1_addition_y,
            done => z1_addition_done
        );

        zn_hadamard_product_enable <= z1_addition_done and n_addition_done;
        zn_hadamard_product_clock <= clock;
        z1_addition_y_address <= zn_hadamard_product_x_1_address;
        n_addition_y_address <= zn_hadamard_product_x_2_address;
        zn_hadamard_product_x_1 <= z1_addition_y;
        zn_hadamard_product_x_2 <= n_tanh_y;
        inst_${name}_zn_hadamard: entity ${work_library_name}.${name}_zn_hadamard(rtl)
        port map (
            enable => zn_hadamard_product_enable,
            clock  => zn_hadamard_product_clock,
            x_1_address  => zn_hadamard_product_x_1_address,
            x_2_address  => zn_hadamard_product_x_2_address,
            y_address  => zn_hadamard_product_y_address,
            x_1  => zn_hadamard_product_x_1,
            x_2  => zn_hadamard_product_x_2,
            y => zn_hadamard_product_y,
            done  => zn_hadamard_product_done
        );

        zh_hadamard_product_enable <= z1_addition_done and z_gate_linear_done and nh_gate_linear_done and zn_hadamard_product_done;
        zh_hadamard_product_clock <= clock;
        zh_hadamard_product_x_1 <= z_sigmoid_y;
        zh_hadamard_product_x_2 <= x_2;
        inst_${name}_zh_hadamard: entity ${work_library_name}.${name}_zh_hadamard(rtl)
        port map (
            enable => zh_hadamard_product_enable,
            clock  => zh_hadamard_product_clock,
            x_1_address  => zh_hadamard_product_x_1_address,
            x_2_address  => zh_hadamard_product_x_2_address,
            y_address  => zh_hadamard_product_y_address,
            x_1  => zh_hadamard_product_x_1,
            x_2  => zh_hadamard_product_x_2,
            y => zh_hadamard_product_y,
            done  => zh_hadamard_product_done
        );

        h_addition_enable <= zh_hadamard_product_done and zn_hadamard_product_done;
        h_addition_clock <= clock;
        zn_hadamard_product_y_address <= h_addition_x_1_address;
        zh_hadamard_product_y_address <= h_addition_x_2_address;
        h_addition_x_1 <= zn_hadamard_product_y;
        h_addition_x_2 <= zh_hadamard_product_y;
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