# Abaqus Subroutine Development Skill

## Skill Description

This skill provides AI-assisted programming guidance for developing Abaqus user subroutines. It includes standardized Fortran code templates, detailed theoretical explanations, and complete engineering examples to help users quickly and accurately develop custom subroutines for finite element analysis.

## Capabilities

- Generate UMAT (User Material) subroutines for custom constitutive models
- Generate VUMAT subroutines for explicit dynamic analysis
- Generate DLOAD/VDLOAD subroutines for distributed moving loads
- Generate DISP/VDISP subroutines for custom displacement boundary conditions
- Generate USDFLD subroutines for spatially varying field variables
- Generate SIGINI subroutines for initial stress conditions
- Generate FRIC/VRIC subroutines for custom friction models
- Generate HETVAL subroutines for heat generation
- Generate UEL/VUEL subroutines for custom elements

## Supported Subroutine Types

| Subroutine | Analysis Type | Purpose |
|------------|--------------|---------|
| UMAT | Standard (Implicit) | Custom material constitutive |
| VUMAT | Explicit | Custom material constitutive |
| DLOAD | Standard | Distributed load definition |
| VDLOAD | Explicit | Distributed load definition |
| DISP | Standard | Custom displacement boundary |
| VDISP | Explicit | Custom displacement boundary |
| USDFLD | General | User-defined field variables |
| SIGINI | General | Initial stress definition |
| SDVINI | General | Initial state variables |
| FRIC | Standard | Custom friction model |
| VRIC | Explicit | Custom friction model |
| HETVAL | Thermal | Heat generation |
| FILM | Thermal | Custom convection |
| UEL | Standard | Custom element |
| VUEL | Explicit | Custom element |

## Usage

### Step 1: Determine Requirements

Before using this skill, clarify:
1. **Analysis Type**: Implicit (Standard) or Explicit?
2. **Physical Phenomenon**: What material behavior or boundary condition needs simulation?
3. **Coupling Requirements**: Do multiple subroutines need to work together?
4. **Complexity**: Linear or highly nonlinear problem?

### Step 2: Select Appropriate Skill

Based on requirements, select the corresponding reference file:

| Requirement | Recommended Reference |
|------------|---------------------|
| Custom material model | `reference/material/umat_*.md` or `reference/material/vumat_*.md` |
| Moving/variable load | `reference/load/dload_moving.md` |
| Vibration/displacement control | `reference/boundary/disp_control.md` |
| Spatially inhomogeneous material | `reference/field/usdfld_spatial.md` |
| Geostress/residual stress | `reference/initial/sigini_stress.md` |
| Tribology problems | `reference/friction/fric_contact.md` |
| Thermal-mechanical coupling | `reference/thermal/hetval_heat.md` + UMAT |
| Special connection elements | `reference/element/uel_spring.md` |

### Step 3: Understand the Skill File

Each skill file contains:
1. **Skill Description**: Applicable scenarios and main functions
2. **Theoretical Formulas**: Mathematical basis and physical models
3. **Interface Definition**: Detailed subroutine parameter descriptions
4. **Code Template**: Complete, ready-to-use Fortran code
5. **Input File Example**: Abaqus keyword reference
6. **Verification Methods**: How to verify implementation correctness
7. **Extension Suggestions**: Directions for further development

### Step 4: Modify and Adapt

Modify the code for your specific problem:

```fortran
C  Modify material parameter section
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      E  = PROPS(1)    ! Modify to your parameter name
      NU = PROPS(2)
      YOUR_PARAM = PROPS(3)  ! Add new parameter
```

### Step 5: Compile and Test

#### Compilation Commands

```bash
# Windows environment
abaqus make library=your_subroutine.f

# Or run job directly
abaqus job=your_job user=your_subroutine.f interactive
```

#### Testing Recommendations

1. **Single Element Test**: Verify constitutive relationship correctness
2. **Simple Boundary Condition Test**: Verify subroutine is correctly called
3. **Benchmark Comparison**: Verify numerical accuracy
4. **Convergence Test**: Verify Jacobian matrix correctness

### Step 6: Debug and Optimize

#### Common Debugging Methods

```fortran
C  Add debug output (note: affects performance)
      WRITE(*,*) 'DEBUG: NOEL=', NOEL, ' STRESS=', STRESS(1)
```

## Best Practices

### Code Standards

1. **Use Fixed-Format Fortran**:
   - Columns 1-5: Statement labels
   - Column 6: Continuation character (non-zero)
   - Columns 7-72: Code body
   - After column 73: Ignored

2. **Variable Declaration**:
```fortran
      REAL*8 E, NU, STRESS(6)    ! Use REAL*8 instead of REAL
      INTEGER I, J, NDI          ! Explicitly declare all variables
```

3. **Constant Definition**:
```fortran
      REAL*8 PI
      PARAMETER(PI=3.141592653589793D0)  ! Use D0 for double precision
```

4. **Error Checking**:
```fortran
C  Parameter range check
      IF (E .LE. 0.0D0) THEN
        WRITE(*,*) 'ERROR: Young modulus must be positive'
        CALL XIT    ! Terminate analysis
      END IF
```

### Performance Optimization

1. **Vectorization for Explicit Subroutines**:
   - VUMAT/VUEL use block loops
   - Avoid scalar operations

2. **Minimize State Variables**:
   - Only store necessary history variables
   - Clean up unused variables promptly

3. **Optimize Matrix Operations**:
   - Utilize matrix symmetry
   - Avoid redundant calculations

### Subroutine Selection Guide

| Problem Type | Recommended Solution | Alternative |
|--------------|---------------------|-------------|
| New constitutive model | UMAT/VUMAT | Built-in material + field variables |
| Moving load | DLOAD/VDLOAD | Multi-node concentrated forces |
| Complex boundary | DISP/VDISP | MPC constraints |
| Non-uniform material | USDFLD+UMAT | Multi-layer material |
| Initial stress | SIGINI | *Initial Conditions |
| Special element | UEL/VUEL | Multi-node connectors |

## Troubleshooting

### Compilation Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Unexpected end of file" | Continuation format error | Check column 6 continuation character |
| "Undefined variable" | Variable not declared | Add type declaration |
| "Type mismatch" | Type inconsistency | Use REAL*8 instead of REAL |
| "Dimension mismatch" | Array dimension error | Check array declaration and access |

### Runtime Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Too many attempts" | Non-convergence | Check Jacobian matrix |
| "Negative eigenvalues" | Stiffness matrix not positive definite | Check material stability |
| "Zero pivot" | Insufficient constraints | Check boundary conditions |
| "NaN in stress" | Numerical overflow | Check division by zero and exponential operations |

### Result Anomalies

| Symptom | Possible Cause | Check Point |
|---------|----------------|-------------|
| Zero stress | STRESS not updated | Check stress update statements |
| Excessive displacement | Stiffness too small | Check material parameter units |
| Non-convergence | Inconsistent Jacobian | Verify DDSDDE derivation |
| Hourglass modes | Reduced integration | Add hourglass control |

## Subroutine Interface Quick Reference

### UMAT (Standard)

```fortran
SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
```

### VUMAT (Explicit)

```fortran
subroutine vumat(
     1 nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2 stepTime, totalTime, dt, cmname, coordMp, charLength,
     3 props, density, strainInc, relSpinInc,
     4 tempOld, stretchOld, defgradOld, fieldOld,
     5 stressOld, stateOld, enerInternOld, enerInelasOld,
     6 tempNew, stretchNew, defgradNew, fieldNew,
     7 stressNew, stateNew, enerInternNew, enerInelasNew)
```

### DLOAD

```fortran
SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
```

### DISP

```fortran
SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
```

### USDFLD

```fortran
SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
```

## Version Information

- Skill Version: 1.0
- Compatible Abaqus Version: 2020 and above
- Fortran Compiler: Intel Fortran 19.0+ or GNU Fortran 9.0+
- Last Updated: 2026-03-20
