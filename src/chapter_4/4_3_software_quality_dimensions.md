## 4.3 Software Quality Dimensions

Software quality can be decomposed along three complementary dimensions.

### Functional Quality

Functional quality measures whether the software correctly implements its intended behaviour. It is evaluated by testing: does the software produce the right outputs for all valid inputs, and behave correctly at boundaries and in error conditions?

### Structural Quality (Non-Functional)

Structural quality measures properties of the system that are not directly visible in outputs but affect long-term viability:

- **Usability**: can users accomplish tasks efficiently with low error rates?
- **Security**: does the system resist known attack vectors?
- **Performance**: does the system meet latency and throughput requirements under load?
- **Maintainability**: can developers understand, modify, and extend the codebase?

### Process Quality

Process quality measures how software is built: are requirements gathered rigorously? Are code reviews conducted? Is CI/CD enforced? A poor process consistently produces poor products, even when individual engineers are skilled.

### ISO 25010 Quality Model

The ISO/IEC 25010 standard ([ISO, 2011 edition](https://www.iso.org/standard/35733.html); revised 2023) defines eight top-level quality characteristics:

| Characteristic | Description |
|---------------|-------------|
| **Functional suitability** | Degree to which functions meet stated and implied needs |
| **Reliability** | Ability to perform specified functions under defined conditions |
| **Performance efficiency** | Performance relative to resources used |
| **Usability** | Effectiveness, efficiency, and satisfaction of use |
| **Security** | Protection of information and data |
| **Maintainability** | Effectiveness with which the product can be modified |
| **Compatibility** | Ability to exchange and use information with other systems |
| **Portability** | Ability to be transferred to different environments |

Each characteristic is further decomposed into sub-characteristics. For example, *reliability* includes fault tolerance, recoverability, and availability.

---
