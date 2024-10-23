"""
Taken from https://github.com/verilog-to-routing/vtr-verilog-to-routing/blob/master/vtr_flow/arch/COFFE_22nm/stratix10_arch.xml, as-is.

Modified:
- Breakable carry chains (set cin_mux_stride = 0 to revert to original)
- LUT skipping in arithmetic mode, and passing adder outputs directly into sneak paths
"""

from structure.arch import ArchFactory
from structure.util import ParamsChecker

TEMPLATE = """<!--
    This is the architecture file for a Stratix-10-like *arithmetic* Architecture discussed in [1].
    The routing architecture is not Stratix-10-like (it is a single wire type of length 4) but 
    the arithmetic inside the logic block is modeled after Stratix 10.
    Delays for routing and logic blocks come from COFFE runs for a 20 nm technology node.
    Delays for DSP blocks come from Arria 10 (22 nm) delays while BRAM delays come from
    Straitx IV (40 nm) delays. In addition, tile grid area comes from COFFE (20 nm) while
    there is no area values provided for the ios, clbs, DSPs, or BRAMs.

    This architecture has 10 ALMs per cluster, where each ALM is a 6-LUT fracturable into
    two 5-LUTs. The ALM has 8 inputs and 4 optionally registered outputs.The two 5-LUTs should
    share at least two inputs. Each two ALM outputs are logically equivalent, which means any
    output signal that can reach ALM.out[0] can reach ALM.out[1] and the same thing for
    ALM.out[2] and ALM.out[3]. The ALMs in this architecture have an arithmetic mode
    where each 5-LUT is fractured into two 4-LUTs, resulting in a total of four 4-LUTs and two
    bits of addition per ALM. This architecture has a single carry chain that spans the 10 ALMs
    in the LAB.

    The LAB has 60 inputs and 40 outputs. Two outputs of each ALM are fed to the right and
    left LAB using direct links and are also fed back to the LAB as feedback connections sharing
    the 60 input ports with the signals coming from the routing channels.

    The architecture also has a 20Kb memory that has true and simple dual port modes. In simple
    dual port mode the memory can be configured in the following modes: 512x40, 1024x20 and 2048x10,
    while in true dual port mode it can be configured as: 1024x20 and 2028x10.

    In addition, the architecture has a 27x27 DSP block that can be fractured into two 18x19 DSPs.


    [1] M. Eldafrawy, A. Boutros, S. Yazdanshenas, and V. Betz, "FPGA Logic Block Architectures for
        Efficient Deep Learning Inference," in Transactions on Reconfigurable Technology and Systems
        (TRETS), 2020

-->
<architecture>
  <!-- 
         ODIN II specific config begins 
         Describes the types of user-specified netlist blocks (in blif, this corresponds to 
         ".model [type_of_block]") that this architecture supports.

         Note: Basic LUTs, I/Os, and flip-flops are not included here as there are 
         already special structures in blif (.names, .input, .output, and .latch) 
         that describe them.
    -->
  <models>
    <model name="multiply">
      <input_ports>
        <port name="a" combinational_sink_ports="out"/>
        <port name="b" combinational_sink_ports="out"/>
      </input_ports>
      <output_ports>
        <port name="out"/>
      </output_ports>
    </model>
    <model name="single_port_ram">
      <input_ports>
        <port name="we" clock="clk"/>
        <!-- control -->
        <port name="addr" clock="clk"/>
        <!-- address lines -->
        <port name="data" clock="clk"/>
        <!-- data lines can be broken down into smaller bit widths minimum size 1 -->
        <port name="clk" is_clock="1"/>
        <!-- memories are often clocked -->
      </input_ports>
      <output_ports>
        <port name="out" clock="clk"/>
        <!-- output can be broken down into smaller bit widths minimum size 1 -->
      </output_ports>
    </model>
    <model name="dual_port_ram">
      <input_ports>
        <port name="we1" clock="clk"/>
        <!-- write enable -->
        <port name="we2" clock="clk"/>
        <!-- write enable -->
        <port name="addr1" clock="clk"/>
        <!-- address lines -->
        <port name="addr2" clock="clk"/>
        <!-- address lines -->
        <port name="data1" clock="clk"/>
        <!-- data lines can be broken down into smaller bit widths minimum size 1 -->
        <port name="data2" clock="clk"/>
        <!-- data lines can be broken down into smaller bit widths minimum size 1 -->
        <port name="clk" is_clock="1"/>
        <!-- memories are often clocked -->
      </input_ports>
      <output_ports>
        <port name="out1" clock="clk"/>
        <!-- output can be broken down into smaller bit widths minimum size 1 -->
        <port name="out2" clock="clk"/>
        <!-- output can be broken down into smaller bit widths minimum size 1 -->
      </output_ports>
    </model>
    <model name="adder">
      <input_ports>
        <port name="a" combinational_sink_ports="cout sumout"/>
        <port name="b" combinational_sink_ports="cout sumout"/>
        <port name="cin" combinational_sink_ports="cout sumout"/>
      </input_ports>
      <output_ports>
        <port name="cout"/>
        <port name="sumout"/>
      </output_ports>
    </model>
  </models>
  <tiles>
    <tile name="io" area="0">
      <sub_tile name="io" capacity="8">
        <equivalent_sites>
          <site pb_type="io" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="outpad" num_pins="1"/>
        <output name="inpad" num_pins="1"/>
        <clock name="clock" num_pins="1"/>
        <fc in_type="frac" in_val="0.15" out_type="frac" out_val="0.10"/>
        <pinlocations pattern="custom">
          <loc side="left">io.outpad io.inpad io.clock</loc>
          <loc side="top">io.outpad io.inpad io.clock</loc>
          <loc side="right">io.outpad io.inpad io.clock</loc>
          <loc side="bottom">io.outpad io.inpad io.clock</loc>
        </pinlocations>
      </sub_tile>
    </tile>
    <tile name="clb">
      <sub_tile name="clb">
        <equivalent_sites>
          <site pb_type="clb" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="I1" num_pins="15"/>
        <input name="I2" num_pins="15"/>
        <input name="I3" num_pins="15"/>
        <input name="I4" num_pins="15"/>
        <input name="cin" num_pins="1"/>
        <output name="O" num_pins="40" equivalent="none"/>
        <output name="cout" num_pins="1"/>
        <clock name="clk" num_pins="1"/>
        <fc in_type="frac" in_val="0.15" out_type="frac" out_val="0.10">
          <fc_override port_name="cin" fc_type="frac" fc_val="0"/>
          <fc_override port_name="cout" fc_type="frac" fc_val="0"/>
        </fc>
        <pinlocations pattern="spread"/>
      </sub_tile>
    </tile>
    <tile name="mult_27" height="2">
      <sub_tile name="mult_27">
        <equivalent_sites>
          <site pb_type="mult_27" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="datain" num_pins="74"/>
        <output name="dataout" num_pins="74"/>
        <fc in_type="frac" in_val="0.15" out_type="frac" out_val="0.10"/>
        <pinlocations pattern="spread"/>
      </sub_tile>
    </tile>
    <tile name="memory" height="4">
      <sub_tile name="memory">
        <equivalent_sites>
          <site pb_type="memory" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="addr1" num_pins="11"/>
        <input name="addr2" num_pins="11"/>
        <input name="data" num_pins="40"/>
        <input name="we1" num_pins="1"/>
        <input name="we2" num_pins="1"/>
        <output name="out" num_pins="40"/>
        <clock name="clk" num_pins="1"/>
        <fc in_type="frac" in_val="0.15" out_type="frac" out_val="0.10"/>
        <pinlocations pattern="spread"/>
      </sub_tile>
    </tile>
  </tiles>
  <!-- ODIN II specific config ends -->
  <layout>
    <!-- Physical descriptions begin -->
    <auto_layout aspect_ratio="1.0">
      <!--Perimeter of 'io' blocks with 'EMPTY' blocks at corners-->
      <perimeter type="io" priority="100"/>
      <corners type="EMPTY" priority="101"/>
      <!--Fill with 'clb'-->
      <fill type="clb" priority="10"/>
      <!--Column of 'mult_27' with 'EMPTY' blocks wherever a 'mult_27' does not fit. Vertical offset by 1 for perimeter.-->
      <col type="mult_27" startx="6" starty="1" repeatx="8" priority="20"/>
      <col type="EMPTY" startx="6" repeatx="8" starty="1" priority="19"/>
      <!--Column of 'memory' with 'EMPTY' blocks wherever a 'memory' does not fit. Vertical offset by 1 for perimeter.-->
      <col type="memory" startx="2" starty="1" repeatx="8" priority="20"/>
      <col type="EMPTY" startx="2" repeatx="8" starty="1" priority="19"/>
    </auto_layout>
  </layout>
  <device>
    <sizing R_minW_nmos="13090" R_minW_pmos="19086.83"/>
    <area grid_logic_tile_area="23678.5"/>
    <chan_width_distr>
      <x distr="uniform" peak="1.000000"/>
      <y distr="uniform" peak="1.000000"/>
    </chan_width_distr>
    <switch_block type="wilton" fs="3"/>
    <connection_block input_switch_name="ipin_cblock"/>
  </device>
  <switchlist>
    <switch type="mux" name="0" R="0.0" Cin="0.0" Cout="0.0" Tdel="230.9e-12" mux_trans_size="2.173" buf_size="36.6"/>
    <switch type="mux" name="ipin_cblock" R="0.0" Cout="0.0" Cin="0.0" Tdel="145e-12" mux_trans_size="1.508" buf_size="11.525"/>
  </switchlist>
  <segmentlist>
    <segment freq="1.000000" length="4" type="unidir" Rmetal="0.0" Cmetal="0.0">
      <mux name="0"/>
      <sb type="pattern">1 1 1 1 1</sb>
      <cb type="pattern">1 1 1 1</cb>
    </segment>
  </segmentlist>
  <directlist>
    <direct name="adder_carry" from_pin="clb.cout" to_pin="clb.cin" x_offset="0" y_offset="-1" z_offset="0"/>
    <!-- Direct connect to left and right LAB -->
    <direct name="direct_right_1" from_pin="clb.O[4:0]" to_pin="clb.I1[9:5]" x_offset="1" y_offset="0" z_offset="0"/>
    <direct name="direct_right_2" from_pin="clb.O[24:20]" to_pin="clb.I2[9:5]" x_offset="1" y_offset="0" z_offset="0"/>
    <direct name="direct_right_3" from_pin="clb.O[9:5]" to_pin="clb.I3[9:5]" x_offset="1" y_offset="0" z_offset="0"/>
    <direct name="direct_right_4" from_pin="clb.O[29:25]" to_pin="clb.I4[9:5]" x_offset="1" y_offset="0" z_offset="0"/>
    <direct name="direct_left_1" from_pin="clb.O[14:10]" to_pin="clb.I1[14:10]" x_offset="-1" y_offset="0" z_offset="0"/>
    <direct name="direct_left_2" from_pin="clb.O[34:30]" to_pin="clb.I2[14:10]" x_offset="-1" y_offset="0" z_offset="0"/>
    <direct name="direct_left_3" from_pin="clb.O[19:15]" to_pin="clb.I3[14:10]" x_offset="-1" y_offset="0" z_offset="0"/>
    <direct name="direct_left_4" from_pin="clb.O[39:35]" to_pin="clb.I4[14:10]" x_offset="-1" y_offset="0" z_offset="0"/>
  </directlist>
  <complexblocklist>
    <!-- Define I/O pads begin -->
    <!-- Capacity is a unique property of I/Os, it is the maximum number of I/Os that can be placed at the same (X,Y) location on the FPGA -->
    <!-- Not sure of the area of an I/O (varies widely), and it's not relevant to the design of the FPGA core, so we're setting it to 0. -->
    <pb_type name="io">
      <input name="outpad" num_pins="1"/>
      <output name="inpad" num_pins="1"/>
      <clock name="clock" num_pins="1"/>
      <!-- IOs can operate as either inputs or outputs.
	     Delays below come from Ian Kuon. They are small, so they should be interpreted as
	     the delays to and from registers in the I/O (and generally I/Os are registered 
	     today and that is when you timing analyze them.
	     -->
      <mode name="inpad">
        <pb_type name="inpad" blif_model=".input" num_pb="1">
          <output name="inpad" num_pins="1"/>
        </pb_type>
        <interconnect>
          <direct name="inpad" input="inpad.inpad" output="io.inpad">
            <delay_constant max="4.243e-11" in_port="inpad.inpad" out_port="io.inpad"/>
          </direct>
        </interconnect>
      </mode>
      <mode name="outpad">
        <pb_type name="outpad" blif_model=".output" num_pb="1">
          <input name="outpad" num_pins="1"/>
        </pb_type>
        <interconnect>
          <direct name="outpad" input="io.outpad" output="outpad.outpad">
            <delay_constant max="1.394e-11" in_port="io.outpad" out_port="outpad.outpad"/>
          </direct>
        </interconnect>
      </mode>
      <!-- Every input pin is driven by 15% of the tracks in a channel, every output pin is driven by 10% of the tracks in a channel -->
      <!-- IOs go on the periphery of the FPGA, for consistency, 
          make it physically equivalent on all sides so that only one definition of I/Os is needed.
          If I do not make a physically equivalent definition, then I need to define 4 different I/Os, one for each side of the FPGA
        -->
      <!-- Place I/Os on the sides of the FPGA -->
      <power method="ignore"/>
    </pb_type>
    <!-- Define I/O pads ends -->
    <!-- Define general purpose logic block (CLB) begin -->
    <pb_type name="clb">
      <input name="I1" num_pins="15"/>
      <input name="I2" num_pins="15"/>
      <input name="I3" num_pins="15"/>
      <input name="I4" num_pins="15"/>
      <input name="cin" num_pins="1"/>
      <output name="O" num_pins="40" equivalent="none"/>
      <output name="cout" num_pins="1"/>
      <clock name="clk" num_pins="1"/>
      <pb_type name="lab" num_pb="1">
        <input name="I1" num_pins="15"/>
        <input name="I2" num_pins="15"/>
        <input name="I3" num_pins="15"/>
        <input name="I4" num_pins="15"/>
        <input name="cin" num_pins="1"/>
        <output name="O" num_pins="40"/>
        <output name="cout" num_pins="1"/>
        <clock name="clk" num_pins="1"/>
        <!-- Describe fracturable logic element.  
                 Each fracturable logic element has a 6-LUT that can alternatively operate as two 5-LUTs with shared inputs. 
                 The outputs of the fracturable logic element can be optionally registered
            -->
        <pb_type name="fle" num_pb="10">
          <input name="in" num_pins="8"/>
          <input name="in_direct" num_pins="4"/>
          <input name="cin" num_pins="1"/>
          <output name="out" num_pins="4"/>
          <output name="cout" num_pins="1"/>
          <clock name="clk" num_pins="1"/>
          <!-- 
                    The ALM inputs are as follows:
                            A -> fle[0]
                            B -> fle[1]
                            C -> fle[2]
                            D -> fle[3]
                            E -> fle[4]
                            F -> fle[5]
                            G -> fle[6]
                            H -> fle[7]
              -->
          <mode name="n2_lut5">
            <pb_type name="ble5" num_pb="2">
              <input name="in" num_pins="5"/>
              <input name="in_direct" num_pins="2"/>
              <input name="cin" num_pins="1"/>
              <output name="out" num_pins="2"/>
              <output name="cout" num_pins="1"/>
              <clock name="clk" num_pins="1"/>
              <!-- Add new arithmetic mode that allows direct connection to adders AND usage of underlying LUT fabric. 
                - Underlying LUT fabric behaves like a normal 5-LUT.
                - Last in[4] is meant to be E/H.
              -->
              <mode name="arithmetic_skip">
                <pb_type name="arithmetic_skip" num_pb="1">
                  <input name="in" num_pins="5"/>
                  <input name="in_direct" num_pins="2"/>
                  <input name="cin" num_pins="1"/>
                  <output name="out" num_pins="2"/>
                  <output name="cout" num_pins="1"/>
                  <clock name="clk" num_pins="1"/>
                  <!-- Normal 5-LUT -->
                  <pb_type name="lut5" blif_model=".names" num_pb="1" class="lut">
                    <input name="in" num_pins="5" port_class="lut_in"/>
                    <output name="out" num_pins="1" port_class="lut_out"/>
                    <!-- LUT timing using delay matrix -->
                    <!-- These are the physical delay inputs on a Stratix 10 LUT but because VPR cannot do LUT rebalancing,
                             we instead take the average of these numbers to get more stable results
                             note that those are the same delays for inputs A - E as the ones used for the 6-LUT, however, we have 
                             subtracted the delay of the last mux stage to get the delay of inputs A - E till the 5-LUT output
                             210.96e-12
                             206.85e-12
                             143.46e-12
                             136.94e-12
                             68.12e-12
                          -->
                    <delay_matrix type="max" in_port="lut5.in" out_port="lut5.out">
                            153.27e-12
                            153.27e-12
                            153.27e-12
                            153.27e-12
                            153.27e-12
                        </delay_matrix>
                  </pb_type>
                  
                  <pb_type name="adder" blif_model=".subckt adder" num_pb="1">
                    <input name="a" num_pins="1"/>
                    <input name="b" num_pins="1"/>
                    <input name="cin" num_pins="1"/>
                    <output name="cout" num_pins="1"/>
                    <output name="sumout" num_pins="1"/>
                    <delay_constant max="68.74e-12" in_port="adder.a" out_port="adder.sumout"/>
                    <delay_constant max="68.74e-12" in_port="adder.b" out_port="adder.sumout"/>
                    <delay_constant max="35.46e-12" in_port="adder.cin" out_port="adder.sumout"/>
                    <delay_constant max="49.32e-12" in_port="adder.a" out_port="adder.cout"/>
                    <delay_constant max="49.32e-12" in_port="adder.b" out_port="adder.cout"/>
                    <delay_constant max="25.56e-12" in_port="adder.cin" out_port="adder.cout"/>
                  </pb_type>
                  
                  <!-- add one more FF to separate adder and LUT outputs. -->
                  <pb_type name="adder_ff" blif_model=".latch" num_pb="1" class="flipflop">
                    <input name="D" num_pins="1" port_class="D"/>
                    <output name="Q" num_pins="1" port_class="Q"/>
                    <clock name="clk" num_pins="1" port_class="clock"/>
                    <T_setup value="18.91e-12" port="adder_ff.D" clock="clk"/>
                    <T_clock_to_Q max="60.32e-12" port="adder_ff.Q" clock="clk"/>
                  </pb_type>
                  <pb_type name="lut5_ff" blif_model=".latch" num_pb="1" class="flipflop">
                    <input name="D" num_pins="1" port_class="D"/>
                    <output name="Q" num_pins="1" port_class="Q"/>
                    <clock name="clk" num_pins="1" port_class="clock"/>
                    <T_setup value="18.91e-12" port="lut5_ff.D" clock="clk"/>
                    <T_clock_to_Q max="60.32e-12" port="lut5_ff.Q" clock="clk"/>
                  </pb_type>
                  <interconnect>
                    <direct name="adder_ff_clock" input="arithmetic_skip.clk" output="adder_ff.clk"/>
                    <direct name="lut5_ff_clock" input="arithmetic_skip.clk" output="lut5_ff.clk"/>
                    <direct name="lut5_in" input="arithmetic_skip.in" output="lut5.in"/>
                    
                    <!-- connect direct input pins to adders directly.
                        - Copy delay of 18.96e-12 from 2-1 muxes in other modes.
                    -->
                    <direct name="to_add1" input="arithmetic_skip.in_direct[0]" output="adder.a">
                      <delay_constant max="18.96e-12" in_port="arithmetic_skip.in_direct[0]" out_port="adder.a"/>
                    </direct>
                    <direct name="to_add2" input="arithmetic_skip.in_direct[1]" output="adder.b">
                      <delay_constant max="18.96e-12" in_port="arithmetic_skip.in_direct[1]" out_port="adder.b"/>
                    </direct>
                    
                    {arith_skip_direct_ff_muxes}
                    
                    <!-- tie to outputs. -->
                    <complete name="sum_out" input="adder_ff.Q adder.sumout" output="arithmetic_skip.out">
                      <delay_constant max="39.85e-12" in_port="adder.sumout" out_port="arithmetic_skip.out"/>
                      <delay_constant max="39.85e-12" in_port="adder_ff.Q" out_port="arithmetic_skip.out"/>
                    </complete>
                    <complete name="lut5_out" input="lut5_ff.Q lut5.out" output="arithmetic_skip.out">
                      <delay_constant max="18.96e-12" in_port="lut5.out" out_port="arithmetic_skip.out"/>
                      <delay_constant max="18.96e-12" in_port="lut5_ff.Q" out_port="arithmetic_skip.out"/>
                    </complete>
                    
                    <!-- carry chain. -->
                    <direct name="carry_in" input="arithmetic_skip.cin" output="adder.cin">
                       <pack_pattern name="chain_skip" in_port="arithmetic_skip.cin" out_port="adder.cin"/> 
                    </direct>
                    <direct name="carry_out" input="adder.cout" output="arithmetic_skip.cout">
                       <pack_pattern name="chain_skip" in_port="adder.cout" out_port="arithmetic_skip.cout"/> 
                    </direct>
                  </interconnect>
                </pb_type>
                <interconnect>
                  <direct name="direct1" input="ble5.in" output="arithmetic_skip.in"/>
                  <direct name="direct2" input="ble5.in_direct" output="arithmetic_skip.in_direct"/>
                  <direct name="carry_in" input="ble5.cin" output="arithmetic_skip.cin">
                     <pack_pattern name="chain_skip" in_port="ble5.cin" out_port="arithmetic_skip.cin"/> 
                  </direct>
                  <direct name="carry_out" input="arithmetic_skip.cout" output="ble5.cout">
                     <pack_pattern name="chain_skip" in_port="arithmetic_skip.cout" out_port="ble5.cout"/> 
                  </direct>
                  <direct name="direct_clk" input="ble5.clk" output="arithmetic_skip.clk"/>
                  <direct name="direct_out" input="arithmetic_skip.out" output="ble5.out"/>
                </interconnect>
              </mode>
              
              <mode name="arithmetic">
                <pb_type name="arithmetic" num_pb="1">
                  <input name="in" num_pins="4"/>
                  <input name="cin" num_pins="1"/>
                  <output name="out" num_pins="2"/>
                  <output name="cout" num_pins="1"/>
                  <clock name="clk" num_pins="1"/>
                  <!-- Special dual-LUT mode that drives adder only -->
                  <pb_type name="lut4" blif_model=".names" num_pb="2" class="lut">
                    <input name="in" num_pins="4" port_class="lut_in"/>
                    <output name="out" num_pins="1" port_class="lut_out"/>
                    <!-- LUT timing using delay matrix -->
                    <!-- These are the physical delay inputs on a Stratix 10 LUT but because VPR cannot do LUT rebalancing,
                           we instead take the average of these numbers to get more stable results
                           note that those are the same delays for inputs A - E as the ones used for the 6-LUT, however, we have 
                           subtracted the delay of the last mux stage to get the delay of inputs A - E till the 5-LUT output
                             168.12e-12
                             164.02e-12
                             100.63e-12
                             94.11e-12
                          -->
                    <delay_matrix type="max" in_port="lut4.in" out_port="lut4.out">
                            131.72e-12
                            131.72e-12
                            131.72e-12
                            131.72e-12
                        </delay_matrix>
                  </pb_type>
                  <pb_type name="adder" blif_model=".subckt adder" num_pb="1">
                    <input name="a" num_pins="1"/>
                    <input name="b" num_pins="1"/>
                    <input name="cin" num_pins="1"/>
                    <output name="cout" num_pins="1"/>
                    <output name="sumout" num_pins="1"/>
                    <delay_constant max="68.74e-12" in_port="adder.a" out_port="adder.sumout"/>
                    <delay_constant max="68.74e-12" in_port="adder.b" out_port="adder.sumout"/>
                    <delay_constant max="35.46e-12" in_port="adder.cin" out_port="adder.sumout"/>
                    <delay_constant max="49.32e-12" in_port="adder.a" out_port="adder.cout"/>
                    <delay_constant max="49.32e-12" in_port="adder.b" out_port="adder.cout"/>
                    <delay_constant max="25.56e-12" in_port="adder.cin" out_port="adder.cout"/>
                  </pb_type>
                  <pb_type name="ff" blif_model=".latch" num_pb="1" class="flipflop">
                    <input name="D" num_pins="1" port_class="D"/>
                    <output name="Q" num_pins="1" port_class="Q"/>
                    <clock name="clk" num_pins="1" port_class="clock"/>
                    <T_setup value="18.91e-12" port="ff.D" clock="clk"/>
                    <T_clock_to_Q max="60.32e-12" port="ff.Q" clock="clk"/>
                  </pb_type>
                  <interconnect>
                    <direct name="clock" input="arithmetic.clk" output="ff.clk"/>
                    <direct name="lut4_in1" input="arithmetic.in" output="lut4[0].in"/>
                    <direct name="lut4_in2" input="arithmetic.in" output="lut4[1].in"/>

                    <!-- add 2-1 mux delay from 4-LUTs to adder inputs. -->
                    <direct name="lut_to_add1" input="lut4[0:0].out" output="adder.a">
                      <delay_constant max="18.96e-12" in_port="lut4[0:0].out" out_port="adder.a"/>
                    </direct>
                    <direct name="lut_to_add2" input="lut4[1:1].out" output="adder.b">
                      <delay_constant max="18.96e-12" in_port="lut4[1:1].out" out_port="adder.b"/>
                    </direct>
                    
                    <direct name="add_to_ff" input="adder.sumout" output="ff.D">
                      <delay_constant max="18.96e-12" in_port="adder.sumout" out_port="ff.D"/>
                      <pack_pattern name="arith_ff" in_port="adder.sumout" out_port="ff.D"/>
                    </direct>
                    <direct name="carry_in" input="arithmetic.cin" output="adder.cin">
                      <pack_pattern name="chain_arith" in_port="arithmetic.cin" out_port="adder.cin"/>
                    </direct>
                    <direct name="carry_out" input="adder.cout" output="arithmetic.cout">
                      <pack_pattern name="chain_arith" in_port="adder.cout" out_port="arithmetic.cout"/>
                    </direct>
                    <complete name="sumout" input="ff.Q adder.sumout" output="arithmetic.out">
                      <delay_constant max="39.85e-12" in_port="adder.sumout" out_port="arithmetic.out"/>
                      <delay_constant max="39.85e-12" in_port="ff.Q" out_port="arithmetic.out"/>
                    </complete>
                  </interconnect>
                </pb_type>
                <interconnect>
                  <direct name="direct1" input="ble5.in[3:0]" output="arithmetic.in"/>
                  <direct name="carry_in" input="ble5.cin" output="arithmetic.cin">
                    <pack_pattern name="chain_arith" in_port="ble5.cin" out_port="arithmetic.cin"/>
                  </direct>
                  <direct name="carry_out" input="arithmetic.cout" output="ble5.cout">
                    <pack_pattern name="chain_arith" in_port="arithmetic.cout" out_port="ble5.cout"/>
                  </direct>
                  <direct name="direct2" input="ble5.clk" output="arithmetic.clk"/>
                  <direct name="direct3" input="arithmetic.out" output="ble5.out"/>
                </interconnect>
              </mode>

              <mode name="blut5">
                <pb_type name="flut5" num_pb="1">
                  <input name="in" num_pins="5"/>
                  <output name="out" num_pins="2"/>
                  <clock name="clk" num_pins="1"/>
                  <!-- Regular LUT mode -->
                  <pb_type name="lut5" blif_model=".names" num_pb="1" class="lut">
                    <input name="in" num_pins="5" port_class="lut_in"/>
                    <output name="out" num_pins="1" port_class="lut_out"/>
                    <!-- LUT timing using delay matrix -->
                    <!-- These are the physical delay inputs on a Stratix 10 LUT but because VPR cannot do LUT rebalancing,
                             we instead take the average of these numbers to get more stable results
                             note that those are the same delays for inputs A - E as the ones used for the 6-LUT, however, we have 
                             subtracted the delay of the last mux stage to get the delay of inputs A - E till the 5-LUT output
                             210.96e-12
                             206.85e-12
                             143.46e-12
                             136.94e-12
                             68.12e-12
                          -->
                    <delay_matrix type="max" in_port="lut5.in" out_port="lut5.out">
                            153.27e-12
                            153.27e-12
                            153.27e-12
                            153.27e-12
                            153.27e-12
                        </delay_matrix>
                  </pb_type>
                  <pb_type name="ff" blif_model=".latch" num_pb="2" class="flipflop">
                    <input name="D" num_pins="1" port_class="D"/>
                    <output name="Q" num_pins="1" port_class="Q"/>
                    <clock name="clk" num_pins="1" port_class="clock"/>
                    <T_setup value="18.91e-12" port="ff.D" clock="clk"/>
                    <T_clock_to_Q max="60.32e-12" port="ff.Q" clock="clk"/>
                  </pb_type>
                  <interconnect>
                    <direct name="lut5_in" input="flut5.in" output="lut5.in"/>
                    <direct name="reg_in" input="flut5.in[0]" output="ff[0].D"/>
                    <direct name="lut5_ff" input="lut5.out" output="ff[1].D">
                      <delay_constant max="18.96e-12" in_port="lut5.out" out_port="ff[1].D"/>
                      <pack_pattern name="ble5_ff" in_port="lut5.out" out_port="ff[1].D"/>
                    </direct>
                    <complete name="clock" input="flut5.clk" output="ff.clk"/>
                    <complete name="out_mux" input="ff.Q lut5.out" output="flut5.out">
                      <delay_constant max="39.85e-12" in_port="lut5.out" out_port="flut5.out"/>
                      <delay_constant max="39.85e-12" in_port="ff.Q" out_port="flut5.out"/>
                    </complete>
                  </interconnect>
                </pb_type>
                <interconnect>
                  <direct name="direct1" input="ble5.in" output="flut5.in"/>
                  <direct name="direct2" input="ble5.clk" output="flut5.clk"/>
                  <direct name="direct3" input="flut5.out" output="ble5.out"/>
                </interconnect>
              </mode>
            </pb_type>
            <interconnect>
              <!-- Shared inputs between the two 5-LUTs -->
              <complete name="lut5_reg1" input="fle.in[0]" output="ble5[0].in[0] ble5[1].in[1]"/>
              <complete name="lut5_reg2" input="fle.in[1]" output="ble5[0].in[1] ble5[1].in[0]"/>
              <!-- Rest of the 5-LUT inputs -->
              <direct name="lut5_inputs_1" input="fle.in[4:2]" output="ble5[0].in[4:2]"/>
              <direct name="lut5_inputs_2" input="fle.in[7:5]" output="ble5[1].in[4:2]"/>
              <direct name="lut5_outputs_1" input="ble5[0].out" output="fle.out[1:0]"/>
              <direct name="lut5_outputs_2" input="ble5[1].out" output="fle.out[3:2]"/>
              <!-- Direct inputs from crossbar -->
              <direct name="lut5_direct1" input="fle.in_direct" output="ble5.in_direct"/>
              
              <direct name="carry_in" input="fle.cin" output="ble5[0].cin">
                <pack_pattern name="chain_skip" in_port="fle.cin" out_port="ble5[0].cin"/>
                <pack_pattern name="chain_arith" in_port="fle.cin" out_port="ble5[0].cin"/>
              </direct>
              <direct name="carry_out" input="ble5[1].cout" output="fle.cout">
                <pack_pattern name="chain_skip" in_port="ble5[1].cout" out_port="fle.cout"/>
                <pack_pattern name="chain_arith" in_port="ble5[1].cout" out_port="fle.cout"/>
              </direct>
              <direct name="carry_link" input="ble5[0].cout" output="ble5[1].cin">
                <pack_pattern name="chain_skip" in_port="ble5[0].cout" out_port="ble5[1].cout"/>
                <pack_pattern name="chain_arith" in_port="ble5[0].cout" out_port="ble5[1].cout"/>
              </direct>
              <complete name="clock" input="fle.clk" output="ble5[1:0].clk"/>
            </interconnect>
          </mode>

          
          <!-- n2_lut5 -->
          <mode name="n1_lut6">
            <pb_type name="ble6" num_pb="1">
              <input name="in" num_pins="6"/>
              <output name="out" num_pins="4"/>
              <clock name="clk" num_pins="1"/>
              <pb_type name="lut6" blif_model=".names" num_pb="1" class="lut">
                <input name="in" num_pins="6" port_class="lut_in"/>
                <output name="out" num_pins="1" port_class="lut_out"/>
                <!-- LUT timing using delay matrix -->
                <!-- These are the physical delay inputs on a Stratix 10 LUT but because VPR cannot do LUT rebalancing,
                           we instead take the average of these numbers to get more stable results
                           257.8e-12
                           253.69e-12
                           190.3e-12
                           183.78e-12
                           114.96e-12
                           77.18e-12
                      -->
                <delay_matrix type="max" in_port="lut6.in" out_port="lut6.out">
                        179.6e-12
                        179.6e-12
                        179.6e-12
                        179.6e-12
                        179.6e-12
                        179.6e-12
                    </delay_matrix>
              </pb_type>
              <pb_type name="ff" blif_model=".latch" num_pb="2" class="flipflop">
                <input name="D" num_pins="1" port_class="D"/>
                <output name="Q" num_pins="1" port_class="Q"/>
                <clock name="clk" num_pins="1" port_class="clock"/>
                <T_setup value="18.91e-12" port="ff.D" clock="clk"/>
                <T_clock_to_Q max="60.32e-12" port="ff.Q" clock="clk"/>
              </pb_type>
              <interconnect>
                <direct name="lut6_inputs" input="ble6.in" output="lut6.in"/>
                <direct name="lut6_ff" input="lut6.out" output="ff[1].D">
                  <delay_constant max="18.96e-12" in_port="lut6.out" out_port="ff[1].D"/>
                  <pack_pattern name="ble6" in_port="lut6.out" out_port="ff[1].D"/>
                </direct>
                <complete name="clock" input="ble6.clk" output="ff.clk"/>
                <direct name="input_to_ff" input="ble6.in[0]" output="ff[0].D"/>
                <mux name="mux1" input="ff[0].Q lut6.out" output="ble6.out[0]">
                  <delay_constant max="39.85e-12" in_port="lut6.out" out_port="ble6.out[0]"/>
                  <delay_constant max="39.85e-12" in_port="ff[0].Q" out_port="ble6.out[0]"/>
                </mux>
                <!-- This mux is the same as mux1 but connected to output 2 -->
                <mux name="mux2" input="ff[0].Q lut6.out" output="ble6.out[1]">
                  <delay_constant max="39.85e-12" in_port="lut6.out" out_port="ble6.out[1]"/>
                  <delay_constant max="39.85e-12" in_port="ff[0].Q" out_port="ble6.out[1]"/>
                </mux>
                <mux name="mux3" input="ff[1].Q lut6.out" output="ble6.out[2]">
                  <delay_constant max="39.85e-12" in_port="lut6.out" out_port="ble6.out[2]"/>
                  <delay_constant max="39.85e-12" in_port="ff[1].Q" out_port="ble6.out[2]"/>
                </mux>
                <!-- This mux is the same as mux2 but connected to output 3 -->
                <mux name="mux4" input="ff[1].Q lut6.out" output="ble6.out[3]">
                  <delay_constant max="39.85e-12" in_port="lut6.out" out_port="ble6.out[3]"/>
                  <delay_constant max="39.85e-12" in_port="ff[1].Q" out_port="ble6.out[3]"/>
                </mux>
              </interconnect>
            </pb_type>
            <interconnect>
              <!-- ble6 takes inputs A, B, C, D, E, & F; where F is fle[7] -->
              <direct name="lut6_inputs1" input="fle.in[4:0]" output="ble6.in[4:0]"/>
              <direct name="lut6_inputs2" input="fle.in[7]" output="ble6.in[5]"/>
              <direct name="direct2" input="ble6.out" output="fle.out"/>
              <direct name="direct4" input="fle.clk" output="ble6.clk"/>
            </interconnect>
          </mode>
          <!-- n1_lut6 -->
        </pb_type>
        <interconnect>
          <!-- 50% sparsely populated local routing, general ALMs -->
          <complete name="lutA" input="lab.I4 lab.I3" output="fle[9:0].in[0:0]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in[0:0]"/>
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in[0:0]"/>
          </complete>
          <complete name="lutB" input="lab.I3 lab.I2" output="fle[9:0].in[1:1]">
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in[1:1]"/>
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in[1:1]"/>
          </complete>
          <complete name="lutC" input="lab.I2 lab.I1" output="fle[9:0].in[2:2]">
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in[2:2]"/>
            <delay_constant max="72.41e-12" in_port="lab.I1" out_port="fle.in[2:2]"/>
          </complete>
          <complete name="lutD" input="lab.I4 lab.I2" output="fle[9:0].in[3:3]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in[3:3]"/>
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in[3:3]"/>
          </complete>
          <complete name="lutE" input="lab.I3 lab.I1" output="fle[9:0].in[4:4]">
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in[4:4]"/>
            <delay_constant max="72.41e-12" in_port="lab.I1" out_port="fle.in[4:4]"/>
          </complete>
          <complete name="lutF" input="lab.I4 lab.I1" output="fle[9:0].in[5:5]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in[5:5]"/>
            <delay_constant max="72.41e-12" in_port="lab.I1" out_port="fle.in[5:5]"/>
          </complete>
          <complete name="lutG" input="lab.I4 lab.I3" output="fle[9:0].in[6:6]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in[6:6]"/>
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in[6:6]"/>
          </complete>
          <complete name="lutH" input="lab.I3 lab.I2" output="fle[9:0].in[7:7]">
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in[7:7]"/>
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in[7:7]"/>
          </complete>
          
          <!-- 50% sparsely populated local routing, direct adder connections -->
          <complete name="lutA_direct" input="lab.I4 lab.I3" output="fle[9:0].in_direct[0:0]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in_direct[0:0]"/>
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in_direct[0:0]"/>
          </complete>
          <complete name="lutB_direct" input="lab.I3 lab.I2" output="fle[9:0].in_direct[1:1]">
            <delay_constant max="72.41e-12" in_port="lab.I3" out_port="fle.in_direct[1:1]"/>
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in_direct[1:1]"/>
          </complete>
          <complete name="lutC_direct" input="lab.I2 lab.I1" output="fle[9:0].in_direct[2:2]">
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in_direct[2:2]"/>
            <delay_constant max="72.41e-12" in_port="lab.I1" out_port="fle.in_direct[2:2]"/>
          </complete>
          <complete name="lutD_direct" input="lab.I4 lab.I2" output="fle[9:0].in_direct[3:3]">
            <delay_constant max="72.41e-12" in_port="lab.I4" out_port="fle.in_direct[3:3]"/>
            <delay_constant max="72.41e-12" in_port="lab.I2" out_port="fle.in_direct[3:3]"/>
          </complete>
          
          <complete name="clks" input="lab.clk" output="fle[9:0].clk"/>
          <!-- This way of specifying direct connection to clb outputs is important because this architecture uses automatic spreading of opins.  
                     By grouping to output pins in this fashion, if a logic block is completely filled by 6-LUTs, 
                     then the outputs those 6-LUTs take get evenly distributed across all four sides of the CLB instead of clumped on two sides (which is what happens with a more
                     naive specification).
              -->
          <direct name="labouts1" input="fle[9:0].out[0]" output="lab.O[9:0]"/>
          <direct name="labouts2" input="fle[9:0].out[1]" output="lab.O[19:10]"/>
          <direct name="labouts3" input="fle[9:0].out[2]" output="lab.O[29:20]"/>
          <direct name="labouts4" input="fle[9:0].out[3]" output="lab.O[39:30]"/>
          <!-- Carry chain links -->
          {carry_chain_links}
        </interconnect>
      </pb_type>
      <interconnect>
        <direct name="carry_in" input="clb.cin" output="lab.cin"/>
        <direct name="carry_out" input="lab.cout" output="clb.cout"/>
        <direct name="clock" input="clb.clk" output="lab.clk"/>
        <complete name="Input_feedback_I1" input="lab.O[4:0]" output="lab.I1"/>
        <complete name="Input_feedback_I2" input="lab.O[24:20]" output="lab.I2"/>
        <complete name="Input_feedback_I3" input="lab.O[9:5]" output="lab.I3"/>
        <complete name="Input_feedback_I4" input="lab.O[29:25]" output="lab.I4"/>
        
        <direct name="Input_I1" input="clb.I1" output="lab.I1"/>
        <direct name="Input_I2" input="clb.I2" output="lab.I2"/>
        <direct name="Input_I3" input="clb.I3" output="lab.I3"/>
        <direct name="Input_I4" input="clb.I4" output="lab.I4"/>
        
        <direct name="output" input="lab.O" output="clb.O"/>
      </interconnect>
    </pb_type>
    <!-- Define general purpose logic block (CLB) ends -->
    <!-- Define fracturable multiplier begin -->
    <pb_type name="mult_27">
      <input name="datain" num_pins="74"/>
      <output name="dataout" num_pins="74"/>
      <mode name="two_mult_18x19">
        <pb_type name="two_mult_18x19" num_pb="2">
          <input name="a" num_pins="18"/>
          <input name="b" num_pins="19"/>
          <output name="out" num_pins="37"/>
          <pb_type name="mult_18x19" blif_model=".subckt multiply" num_pb="1">
            <input name="a" num_pins="18"/>
            <input name="b" num_pins="19"/>
            <output name="out" num_pins="37"/>
            <!-- Using the numbers from Arria 10 which is a 22nm technology, an 18x19 multiplier 
                    can operate at 548 MHz which maps to a delay of 1.825e-9 -->
            <delay_constant max="1.825e-9" in_port="mult_18x19.a" out_port="mult_18x19.out"/>
            <delay_constant max="1.825e-9" in_port="mult_18x19.b" out_port="mult_18x19.out"/>
          </pb_type>
          <interconnect>
            <direct name="a2a" input="two_mult_18x19.a" output="mult_18x19.a">
               </direct>
            <direct name="b2b" input="two_mult_18x19.b" output="mult_18x19.b">
               </direct>
            <direct name="out2out" input="mult_18x19.out" output="two_mult_18x19.out">
               </direct>
          </interconnect>
          <power method="pin-toggle">
            <port name="a" energy_per_toggle="1.09e-12"/>
            <port name="b" energy_per_toggle="1.09e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="datain2a1" input="mult_27.datain[17:0]" output="two_mult_18x19[0].a">
            <delay_constant max="134e-12" in_port="mult_27.datain[17:0]" out_port="two_mult_18x19[0].a"/>
          </direct>
          <direct name="datain2b1" input="mult_27.datain[36:18]" output="two_mult_18x19[0].b">
            <delay_constant max="134e-12" in_port="mult_27.datain[36:18]" out_port="two_mult_18x19[0].b"/>
          </direct>
          <direct name="datain2a2" input="mult_27.datain[54:37]" output="two_mult_18x19[1].a">
            <delay_constant max="134e-12" in_port="mult_27.datain[54:37]" out_port="two_mult_18x19[1].a"/>
          </direct>
          <direct name="datain2b2" input="mult_27.datain[73:55]" output="two_mult_18x19[1].b">
            <delay_constant max="134e-12" in_port="mult_27.datain[73:55]" out_port="two_mult_18x19[1].b"/>
          </direct>
          <direct name="out2dataout" input="two_mult_18x19[1:0].out" output="mult_27.dataout">
            <delay_constant max="1.09e-9" in_port="two_mult_18x19[1:0].out" out_port="mult_27.dataout"/>
          </direct>
        </interconnect>
      </mode>
      <mode name="mult_27x27">
        <pb_type name="one_mult_27x27" num_pb="1">
          <input name="a" num_pins="27"/>
          <input name="b" num_pins="27"/>
          <output name="out" num_pins="54"/>
          <pb_type name="mult_27x27" blif_model=".subckt multiply" num_pb="1">
            <input name="a" num_pins="27"/>
            <input name="b" num_pins="27"/>
            <output name="out" num_pins="54"/>
            <!-- Using the numbers from Arria 10 which is a 22nm technology, an 27x27 multiplier 
                    can operate at 541 MHz which maps to a delay of 1.848e-9 -->
            <delay_constant max="1.848e-9" in_port="mult_27x27.a" out_port="mult_27x27.out"/>
            <delay_constant max="1.848e-9" in_port="mult_27x27.b" out_port="mult_27x27.out"/>
          </pb_type>
          <interconnect>
            <direct name="a2a" input="one_mult_27x27.a" output="mult_27x27.a">
               </direct>
            <direct name="b2b" input="one_mult_27x27.b" output="mult_27x27.b">
               </direct>
            <direct name="out2out" input="mult_27x27.out" output="one_mult_27x27.out">
               </direct>
          </interconnect>
          <power method="pin-toggle">
            <port name="a" energy_per_toggle="2.13e-12"/>
            <port name="b" energy_per_toggle="2.13e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="datain2a" input="mult_27.datain[26:0]" output="one_mult_27x27.a">
            <delay_constant max="134e-12" in_port="mult_27.datain[26:0]" out_port="one_mult_27x27.a"/>
          </direct>
          <direct name="datain2b" input="mult_27.datain[53:27]" output="one_mult_27x27.b">
            <delay_constant max="134e-12" in_port="mult_27.datain[53:27]" out_port="one_mult_27x27.b"/>
          </direct>
          <direct name="out2dataout" input="one_mult_27x27.out" output="mult_27.dataout[53:0]">
            <delay_constant max="1.93e-9" in_port="one_mult_27x27.out" out_port="mult_27.dataout[53:0]"/>
          </direct>
        </interconnect>
      </mode>
      <!-- Place this multiplier block every 8 columns from (and including) the sixth column -->
      <power method="sum-of-children"/>
    </pb_type>
    <!-- Define fracturable multiplier end -->
    <!-- Define fracturable memory begin -->
    <pb_type name="memory">
      <input name="addr1" num_pins="11"/>
      <input name="addr2" num_pins="11"/>
      <input name="data" num_pins="40"/>
      <input name="we1" num_pins="1"/>
      <input name="we2" num_pins="1"/>
      <output name="out" num_pins="40"/>
      <clock name="clk" num_pins="1"/>
      <!-- Specify single port mode first -->
      <mode name="mem_512x40_sp">
        <pb_type name="mem_512x40_sp" blif_model=".subckt single_port_ram" class="memory" num_pb="1">
          <input name="addr" num_pins="9" port_class="address"/>
          <input name="data" num_pins="40" port_class="data_in"/>
          <input name="we" num_pins="1" port_class="write_en"/>
          <output name="out" num_pins="40" port_class="data_out"/>
          <clock name="clk" num_pins="1" port_class="clock"/>
          <T_setup value="509e-12" port="mem_512x40_sp.addr" clock="clk"/>
          <T_setup value="509e-12" port="mem_512x40_sp.data" clock="clk"/>
          <T_setup value="509e-12" port="mem_512x40_sp.we" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_512x40_sp.out" clock="clk"/>
          <power method="pin-toggle">
            <port name="clk" energy_per_toggle="9.0e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="address1" input="memory.addr1[8:0]" output="mem_512x40_sp.addr">
            <delay_constant max="132e-12" in_port="memory.addr1[8:0]" out_port="mem_512x40_sp.addr"/>
          </direct>
          <direct name="data1" input="memory.data" output="mem_512x40_sp.data">
            <delay_constant max="132e-12" in_port="memory.data" out_port="mem_512x40_sp.data"/>
          </direct>
          <direct name="writeen1" input="memory.we1" output="mem_512x40_sp.we">
            <delay_constant max="132e-12" in_port="memory.we1" out_port="mem_512x40_sp.we"/>
          </direct>
          <direct name="dataout1" input="mem_512x40_sp.out" output="memory.out">
            <delay_constant max="40e-12" in_port="mem_512x40_sp.out" out_port="memory.out"/>
          </direct>
          <direct name="clk" input="memory.clk" output="mem_512x40_sp.clk">
             </direct>
        </interconnect>
      </mode>
      <mode name="mem_1024x20_sp">
        <pb_type name="mem_1024x20_sp" blif_model=".subckt single_port_ram" class="memory" num_pb="1">
          <input name="addr" num_pins="10" port_class="address"/>
          <input name="data" num_pins="20" port_class="data_in"/>
          <input name="we" num_pins="1" port_class="write_en"/>
          <output name="out" num_pins="20" port_class="data_out"/>
          <clock name="clk" num_pins="1" port_class="clock"/>
          <T_setup value="509e-12" port="mem_1024x20_sp.addr" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_sp.data" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_sp.we" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_1024x20_sp.out" clock="clk"/>
          <power method="pin-toggle">
            <port name="clk" energy_per_toggle="9.0e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="address1" input="memory.addr1[9:0]" output="mem_1024x20_sp.addr">
            <delay_constant max="132e-12" in_port="memory.addr1[9:0]" out_port="mem_1024x20_sp.addr"/>
          </direct>
          <direct name="data1" input="memory.data[19:0]" output="mem_1024x20_sp.data">
            <delay_constant max="132e-12" in_port="memory.data[19:0]" out_port="mem_1024x20_sp.data"/>
          </direct>
          <direct name="writeen1" input="memory.we1" output="mem_1024x20_sp.we">
            <delay_constant max="132e-12" in_port="memory.we1" out_port="mem_1024x20_sp.we"/>
          </direct>
          <direct name="dataout1" input="mem_1024x20_sp.out" output="memory.out[19:0]">
            <delay_constant max="40e-12" in_port="mem_1024x20_sp.out" out_port="memory.out[19:0]"/>
          </direct>
          <direct name="clk" input="memory.clk" output="mem_1024x20_sp.clk">
             </direct>
        </interconnect>
      </mode>
      <mode name="mem_2048x10_sp">
        <pb_type name="mem_2048x10_sp" blif_model=".subckt single_port_ram" class="memory" num_pb="1">
          <input name="addr" num_pins="11" port_class="address"/>
          <input name="data" num_pins="10" port_class="data_in"/>
          <input name="we" num_pins="1" port_class="write_en"/>
          <output name="out" num_pins="10" port_class="data_out"/>
          <clock name="clk" num_pins="1" port_class="clock"/>
          <T_setup value="509e-12" port="mem_2048x10_sp.addr" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_sp.data" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_sp.we" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_2048x10_sp.out" clock="clk"/>
          <power method="pin-toggle">
            <port name="clk" energy_per_toggle="9.0e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="address1" input="memory.addr1[10:0]" output="mem_2048x10_sp.addr">
            <delay_constant max="132e-12" in_port="memory.addr1[10:0]" out_port="mem_2048x10_sp.addr"/>
          </direct>
          <direct name="data1" input="memory.data[9:0]" output="mem_2048x10_sp.data">
            <delay_constant max="132e-12" in_port="memory.data[9:0]" out_port="mem_2048x10_sp.data"/>
          </direct>
          <direct name="writeen1" input="memory.we1" output="mem_2048x10_sp.we">
            <delay_constant max="132e-12" in_port="memory.we1" out_port="mem_2048x10_sp.we"/>
          </direct>
          <direct name="dataout1" input="mem_2048x10_sp.out" output="memory.out[9:0]">
            <delay_constant max="40e-12" in_port="mem_2048x10_sp.out" out_port="memory.out[9:0]"/>
          </direct>
          <direct name="clk" input="memory.clk" output="mem_2048x10_sp.clk">
             </direct>
        </interconnect>
      </mode>
      <!-- Specify true dual port mode next -->
      <mode name="mem_1024x20_dp">
        <pb_type name="mem_1024x20_dp" blif_model=".subckt dual_port_ram" class="memory" num_pb="1">
          <input name="addr1" num_pins="10" port_class="address1"/>
          <input name="addr2" num_pins="10" port_class="address2"/>
          <input name="data1" num_pins="20" port_class="data_in1"/>
          <input name="data2" num_pins="20" port_class="data_in2"/>
          <input name="we1" num_pins="1" port_class="write_en1"/>
          <input name="we2" num_pins="1" port_class="write_en2"/>
          <output name="out1" num_pins="20" port_class="data_out1"/>
          <output name="out2" num_pins="20" port_class="data_out2"/>
          <clock name="clk" num_pins="1" port_class="clock"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.addr1" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.data1" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.we1" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.addr2" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.data2" clock="clk"/>
          <T_setup value="509e-12" port="mem_1024x20_dp.we2" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_1024x20_dp.out1" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_1024x20_dp.out2" clock="clk"/>
          <power method="pin-toggle">
            <port name="clk" energy_per_toggle="17.9e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="address1" input="memory.addr1[9:0]" output="mem_1024x20_dp.addr1">
            <delay_constant max="132e-12" in_port="memory.addr1[9:0]" out_port="mem_1024x20_dp.addr1"/>
          </direct>
          <direct name="address2" input="memory.addr2[9:0]" output="mem_1024x20_dp.addr2">
            <delay_constant max="132e-12" in_port="memory.addr2[9:0]" out_port="mem_1024x20_dp.addr2"/>
          </direct>
          <direct name="data1" input="memory.data[19:0]" output="mem_1024x20_dp.data1">
            <delay_constant max="132e-12" in_port="memory.data[19:0]" out_port="mem_1024x20_dp.data1"/>
          </direct>
          <direct name="data2" input="memory.data[39:20]" output="mem_1024x20_dp.data2">
            <delay_constant max="132e-12" in_port="memory.data[39:20]" out_port="mem_1024x20_dp.data2"/>
          </direct>
          <direct name="writeen1" input="memory.we1" output="mem_1024x20_dp.we1">
            <delay_constant max="132e-12" in_port="memory.we1" out_port="mem_1024x20_dp.we1"/>
          </direct>
          <direct name="writeen2" input="memory.we2" output="mem_1024x20_dp.we2">
            <delay_constant max="132e-12" in_port="memory.we2" out_port="mem_1024x20_dp.we2"/>
          </direct>
          <direct name="dataout1" input="mem_1024x20_dp.out1" output="memory.out[19:0]">
            <delay_constant max="40e-12" in_port="mem_1024x20_dp.out1" out_port="memory.out[19:0]"/>
          </direct>
          <direct name="dataout2" input="mem_1024x20_dp.out2" output="memory.out[39:20]">
            <delay_constant max="40e-12" in_port="mem_1024x20_dp.out2" out_port="memory.out[39:20]"/>
          </direct>
          <direct name="clk" input="memory.clk" output="mem_1024x20_dp.clk">
             </direct>
        </interconnect>
      </mode>
      <mode name="mem_2048x10_dp">
        <pb_type name="mem_2048x10_dp" blif_model=".subckt dual_port_ram" class="memory" num_pb="1">
          <input name="addr1" num_pins="11" port_class="address1"/>
          <input name="addr2" num_pins="11" port_class="address2"/>
          <input name="data1" num_pins="10" port_class="data_in1"/>
          <input name="data2" num_pins="10" port_class="data_in2"/>
          <input name="we1" num_pins="1" port_class="write_en1"/>
          <input name="we2" num_pins="1" port_class="write_en2"/>
          <output name="out1" num_pins="10" port_class="data_out1"/>
          <output name="out2" num_pins="10" port_class="data_out2"/>
          <clock name="clk" num_pins="1" port_class="clock"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.addr1" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.data1" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.we1" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.addr2" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.data2" clock="clk"/>
          <T_setup value="509e-12" port="mem_2048x10_dp.we2" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_2048x10_dp.out1" clock="clk"/>
          <T_clock_to_Q max="1.234e-9" port="mem_2048x10_dp.out2" clock="clk"/>
          <power method="pin-toggle">
            <port name="clk" energy_per_toggle="17.9e-12"/>
            <static_power power_per_instance="0.0"/>
          </power>
        </pb_type>
        <interconnect>
          <direct name="address1" input="memory.addr1[10:0]" output="mem_2048x10_dp.addr1">
            <delay_constant max="132e-12" in_port="memory.addr1[10:0]" out_port="mem_2048x10_dp.addr1"/>
          </direct>
          <direct name="address2" input="memory.addr2[10:0]" output="mem_2048x10_dp.addr2">
            <delay_constant max="132e-12" in_port="memory.addr2[10:0]" out_port="mem_2048x10_dp.addr2"/>
          </direct>
          <direct name="data1" input="memory.data[9:0]" output="mem_2048x10_dp.data1">
            <delay_constant max="132e-12" in_port="memory.data[9:0]" out_port="mem_2048x10_dp.data1"/>
          </direct>
          <direct name="data2" input="memory.data[19:10]" output="mem_2048x10_dp.data2">
            <delay_constant max="132e-12" in_port="memory.data[19:10]" out_port="mem_2048x10_dp.data2"/>
          </direct>
          <direct name="writeen1" input="memory.we1" output="mem_2048x10_dp.we1">
            <delay_constant max="132e-12" in_port="memory.we1" out_port="mem_2048x10_dp.we1"/>
          </direct>
          <direct name="writeen2" input="memory.we2" output="mem_2048x10_dp.we2">
            <delay_constant max="132e-12" in_port="memory.we2" out_port="mem_2048x10_dp.we2"/>
          </direct>
          <direct name="dataout1" input="mem_2048x10_dp.out1" output="memory.out[9:0]">
            <delay_constant max="40e-12" in_port="mem_2048x10_dp.out1" out_port="memory.out[9:0]"/>
          </direct>
          <direct name="dataout2" input="mem_2048x10_dp.out2" output="memory.out[19:10]">
            <delay_constant max="40e-12" in_port="mem_2048x10_dp.out2" out_port="memory.out[19:10]"/>
          </direct>
          <direct name="clk" input="memory.clk" output="mem_2048x10_dp.clk">
             </direct>
        </interconnect>
      </mode>
      <!-- Every input pin is driven by 15% of the tracks in a channel, every output pin is driven by 10% of the tracks in a channel -->
      <!-- Place this memory block every 8 columns from (and including) the second column -->
      <power method="sum-of-children"/>
    </pb_type>
    <!-- Define fracturable memory end -->
  </complexblocklist>
  <power>
    <local_interconnect C_wire="2.5e-10"/>
    <mux_transistor_size mux_transistor_size="3"/>
    <FF_size FF_size="4"/>
    <LUT_transistor_size LUT_transistor_size="4"/>
  </power>
  <clocks>
    <clock buffer_size="auto" C_wire="2.5e-10"/>
  </clocks>
</architecture>
"""

def gen_carry_chain_links(ble_count=10, mux_stride=1):
    # mux inputs from FLE 2 - N
    mux_ins = ''
    if ble_count > 1:
        mux_ins_strs = []
        for x in range(1, ble_count):
          is_mux = x % mux_stride == 0 if mux_stride > 0 else False
          tag = 'mux' if is_mux else 'direct'
          
          # TO-DO: adjust mux delay
          tag_delay = '1.679e-12' if is_mux else '1.679e-12'
          
          mux_delay_lab = f'<delay_constant max="{tag_delay}" in_port="lab.cin" out_port="fle[{x}:{x}].cin"/>\n            ' if is_mux else ''
          mux_ins_strs.append(f"""          <{tag} name="cin{x}" input="{'lab.cin ' if is_mux else ''}fle[{x-1}:{x-1}].cout" output="fle[{x}:{x}].cin">
            {mux_delay_lab}<delay_constant max="{tag_delay}" in_port="fle[{x-1}:{x-1}].cout" out_port="fle[{x}:{x}].cin"/>
          </{tag}>
""")
          mux_ins = '\n'.join(mux_ins_strs)

    return f"""
          <direct name="carry_in" input="lab.cin" output="fle[0:0].cin">
            <delay_constant max="1.679e-12" in_port="lab.cin" out_port="fle[0:0].cin"/>
            <pack_pattern name="chain_skip" in_port="lab.cin" out_port="fle[0:0].cin"/>
            <pack_pattern name="chain_arith" in_port="lab.cin" out_port="fle[0:0].cin"/>
          </direct>
{mux_ins}
<direct name="couts" input="fle[{ble_count-1}:{ble_count-1}].cout" output="lab.cout">
    <pack_pattern name="chain_skip" in_port="fle[{ble_count-1}:{ble_count-1}].cout" out_port="lab.cout"/>
    <pack_pattern name="chain_arith" in_port="fle[{ble_count-1}:{ble_count-1}].cout" out_port="lab.cout"/>
</direct>
"""   

def gen_arith_skip_direct_ff_muxes(direct_ff_mux_with='lut'):
    if direct_ff_mux_with == 'adder':
        return """
                    <!-- mux register-only input or adder output to first FF. -->
                    <mux name="add_to_ff" input="arithmetic_skip.in[0] adder.sumout" output="adder_ff.D">
                      <delay_constant max="18.96e-12" in_port="arithmetic_skip.in[0]" out_port="adder_ff.D"/>
                      <delay_constant max="18.96e-12" in_port="adder.sumout" out_port="adder_ff.D"/>
                    </mux>
                    <!-- 5-LUT output to second FF. -->
                    <direct name="lut5_to_ff" input="lut5.out" output="lut5_ff.D">
                      <delay_constant max="18.96e-12" in_port="lut5.out" out_port="lut5_ff.D"/>
                      <pack_pattern name="lut5_ff" in_port="lut5.out" out_port="lut5_ff.D"/>
                    </direct>
"""

    # return at 5-LUT by default.
    return """
                    <!-- adder output to first FF. -->
                    <direct name="add_to_ff" input="adder.sumout" output="adder_ff.D">
                      <delay_constant max="18.96e-12" in_port="adder.sumout" out_port="adder_ff.D"/>
                      <pack_pattern name="adder_ff" in_port="adder.sumout" out_port="adder_ff.D"/>
                    </direct>
                    <!-- mux register-only input or 5-LUT output to second FF. -->
                    <mux name="lut5_to_ff" input="arithmetic_skip.in[0] lut5.out" output="lut5_ff.D">
                      <delay_constant max="18.96e-12" in_port="arithmetic_skip.in[0]" out_port="lut5_ff.D"/>
                      <delay_constant max="18.96e-12" in_port="lut5.out" out_port="lut5_ff.D"/>
                    </mux>
"""     
    

DEFAULTS = {
    'cin_mux_stride': 1, # insert a 2:1 MUX in the carry chain every ? ALMs.

    # in arithmetic_skip mode, define whether the input that connects directly to the FFs (A/B) is MUXed with:
    # - 'adder': the adder output, or
    # - 'lut': the 5-LUT equivalent output (default).
    'direct_ff_mux_with': 'lut', 
}

class LUTSkipArchFactory(ArchFactory, ParamsChecker):
    def get_name(self, cin_mux_stride: int, direct_ff_mux_with: str, **kwargs):
        return f"type.s10-skip_cin.{cin_mux_stride}_ff.{direct_ff_mux_with}"
    
    def verify_params(self, params):
        return self.verify_required_keys(DEFAULTS, [], params)
    
    def get_arch(self, cin_mux_stride: int, direct_ff_mux_with: str, **kwargs):
        return TEMPLATE.format(
            carry_chain_links=gen_carry_chain_links(mux_stride=cin_mux_stride),
            arith_skip_direct_ff_muxes=gen_arith_skip_direct_ff_muxes(direct_ff_mux_with=direct_ff_mux_with),
        )