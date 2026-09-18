-- All tables stay portrait and can break across pages in the prose flow.
function Pandoc(doc)
  local out = pandoc.List()
  local function raw(s) out:insert(pandoc.RawBlock('latex',s)) end
  for _,block in ipairs(doc.blocks) do
    if block.t == 'Table' then
      local count = #block.colspecs
      local matrix = pandoc.utils.stringify(block.head):find('模块及作用')
      local widths = matrix and count == 5 and {.19,.24,.21,.26,.10} or nil
      for i,spec in ipairs(block.colspecs) do
        spec[1] = pandoc.AlignLeft
        spec[2] = .99 * (widths and widths[i] or 1/count)
      end
      -- Permit native inline math to wrap at operators inside narrow cells.
      block = block:walk({Math = function(el)
        el.text = el.text:gsub('\\times', '\\times\\allowbreak ')
                         :gsub('\\to([^%a])', '\\to\\allowbreak %1')
                         :gsub('=', '=\\allowbreak ')
                         :gsub('%+', '+\\allowbreak ')
        return el
      end})
      local rows = 0
      for _,body in ipairs(block.bodies) do rows=rows+#body.body+#body.head end
      if rows <= 12 then
        local title=out[#out]
        if title and title.t=='Para' and title.content[1] and title.content[1].t=='Strong'
            and #pandoc.utils.stringify(title)<220 then out:remove(#out) else title=nil end
        -- Inline, nonfloating short tables avoid longtable's output routine.
        local tex=pandoc.write(pandoc.Pandoc({block}), 'latex')
        tex=tex:gsub('\\begin{longtable}%[%]', '\\begin{tabular}')
        tex=tex:gsub('\\endhead%s*\\bottomrule\\noalign{}%s*\\endlastfoot', '')
        tex=tex:gsub('\\end{longtable}', '\\bottomrule\\end{tabular}')
        raw('\\par\\addvspace{6pt}\\noindent\\begin{minipage}{\\linewidth}\\begin{infratable}')
        if title then out:insert(title);raw('\\par\\smallskip') end
        raw(tex)
        raw('\\end{infratable}\\end{minipage}\\par\\addvspace{6pt}')
      else
        raw('\\begin{infratable}')
        out:insert(block)
        raw('\\end{infratable}')
      end
    elseif block.t == 'Figure' then
      -- Figures float freely ([!htbp]); no barrier anywhere, so prose keeps
      -- filling each page and LaTeX places the figure at the next opportunity.
      out:insert(block)
    else out:insert(block) end
  end
  doc.blocks=out
  return doc
end
function Math(el)
  -- Keep Greek mu in math mode; \mathrm text fonts lack its math Unicode glyph.
  el.text = el.text:gsub('\\mathrm{%s*\\mu%s*s}', '\\mu\\,\\mathrm{s}')
  return el
end
function Header(el)
  if el.level > 1 and not pandoc.utils.stringify(el):match('^%d') then
    el.classes:insert('unnumbered')
  end
  -- Source numbers are removed only after deciding whether it is a numbered heading.
  local inlines = el.content
  if el.level == 1 then
    -- Preprocessor has removed the Chinese chapter prefix.
    return el
  end
  if inlines[1] and inlines[1].t == 'Str' and inlines[1].text:match('^%d+%.') then
    inlines:remove(1)
    if inlines[1] and inlines[1].t == 'Space' then inlines:remove(1) end
  end
  return el
end

-- Keep image scaling local to graphics; math never passes through graphicx.
function Image(el)
  -- The sixteen-chapter roadmap is drawn at book width with readable labels.
  -- Keep that reading size instead of shrinking it like a small inline diagram.
  if el.src:match('figure%-1%-book%-roadmap%.') then
    return pandoc.RawInline('latex', '\\includegraphics[width=.95\\linewidth,height=.60\\textheight,keepaspectratio]{' .. el.src .. '}')
  end
  return pandoc.RawInline('latex', '\\infragraphic{' .. el.src .. '}')
end
