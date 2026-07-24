export const meta = {
  name: 'arm-translate-batches',
  description: '把 ARM A64 特性描述与指令简述批量翻译成简体中文，写出 out_*.json',
  phases: [
    { title: 'Features', detail: '逐批翻译 FEAT_* 中文介绍' },
    { title: 'Instructions', detail: '逐批翻译指令中文一行简介' },
  ],
}

// 批次目录与数量随数据集环境而变；Workflow 脚本运行时无 fs/env/cwd 访问，
// 故不在脚本内硬编码任何本地路径——改由调用方每次运行时按当前环境传入批次清单（“根据环境确认”）。
// 来源：prep_translate.py 会在 <当前仓库>/skill_build/desc/manifest.json 写出
//   { feat: [{in, out}, ...], instr: [{in, out}, ...] }（绝对路径已按当前环境生成）；
//   调用 Workflow 时把该 manifest 的内容作为 args 传入即可。
// 备选：若运行时取不到 args，可在此处直接内联当前环境的 manifest 对象来替代 `args`。
if (!args || !Array.isArray(args.feat) || !Array.isArray(args.instr)) {
  throw new Error('请通过 args 传入当前环境的批次清单 { feat:[{in,out}...], instr:[{in,out}...] }（取自 skill_build/desc/manifest.json）')
}
const featBatches = args.feat
const instrBatches = args.instr

const featPrompt = (b) => `你是 ARM 架构资料的中英翻译专家。请把一批 ARM A-profile 架构特性的英文描述翻译成简体中文功能介绍，用于查阅表。

步骤：
1. 用 Read 工具读取这个 JSON 数组文件：${b.in}
   每个元素形如 {name, title, before, after}。
2. 对每个元素，写一段简体中文「中文介绍」：1~3 句，准确概括该特性的功能与用途。
   - 主要依据 before（功能描述）和 title；after 含版本/依赖信息，仅作背景参考，不要照搬。
   - 保留专有名词/缩写的英文：如 SVE、SME、PMU、ASID、ZA、PAC、MTE、TLB、EL0~EL3、GIC 等。
   - 技术准确、表达自然；不要逐字直译，不要保留 "-" 列表符号，不要输出版本号当正文。
   - 若 before 为空，则根据 title 概括其含义。
3. 用 Write 工具把结果写到：${b.out}
   内容是一个 JSON 对象，键为每个元素的 name，值为对应中文介绍字符串。
   必须只写纯 JSON（不要 markdown 代码块、不要任何解释文字），UTF-8，中文直接写出。
   对象的键必须与输入的全部 name 一一对应，不可遗漏。

完成后，最终消息只回复：ok <写出的条目数>`

const instrPrompt = (b) => `你是 ARM 架构资料的中英翻译专家。请把一批 ARM A64 指令的英文一行简述翻译成简体中文一行简介，用于查阅表。

步骤：
1. 用 Read 工具读取这个 JSON 数组文件：${b.in}
   每个元素形如 {id, heading, brief}。
2. 对每个元素，写一句简体中文「一行简介」（尽量 ≤ 25 字），准确描述该指令作用，依据 brief 与 heading。
   - 保留必要的术语/缩写英文：如 SIMD、SVE、SME、ZA、PC、SP、NZCV、FPSR 等。
   - 别名指令（brief 含 "an alias of X"）译为「<功能>（X 的别名）」。
   - 简洁、准确、统一风格；不要输出多余解释。
3. 用 Write 工具把结果写到：${b.out}
   内容是一个 JSON 对象，键为每个元素的 id，值为对应中文一行简介。
   必须只写纯 JSON（不要 markdown 代码块、不要任何解释文字），UTF-8，中文直接写出。
   对象的键必须与输入的全部 id 一一对应，不可遗漏。

完成后，最终消息只回复：ok <写出的条目数>`

phase('Features')
const featResults = await parallel(featBatches.map((b, i) => () =>
  agent(featPrompt(b), {
    label: `feat:${i}`, phase: 'Features',
    agentType: 'general-purpose', model: 'sonnet',
  })))

phase('Instructions')
const instrResults = await parallel(instrBatches.map((b, i) => () =>
  agent(instrPrompt(b), {
    label: `instr:${i}`, phase: 'Instructions',
    agentType: 'general-purpose', model: 'sonnet',
  })))

log(`feat 批完成 ${featResults.filter(Boolean).length}/${featBatches.length}, instr 批完成 ${instrResults.filter(Boolean).length}/${instrBatches.length}`)
return { feat: featResults, instr: instrResults }
