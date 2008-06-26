"
" Max E. Kuznecov ~syhpoon <syhpoon@syhpoon.name> 2008
"
" This file is part of XYZCommander.
" XYZCommander is free software: you can redistribute it and/or modify
" it under the terms of the GNU Lesser Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
" XYZCommander is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
" GNU Lesser Public License for more details.
" You should have received a copy of the GNU Lesser Public License
" along with XYZCommander. If not, see <http://www.gnu.org/licenses/>.

"
" conf/keys syntax file
"

setlocal iskeyword+=!

syn case match

syn match xyzComment /#.*/
"syn keyword xyzKeyword context
syn match xyzContext /context\s\+\(@\|\w\+\)/

"""load :ns:plugin
syn match xyzLoad /load/ nextgroup=xyzNSPath skipwhite
syn match xyzNSPath /\(\:[^ ]\+\)/ contained skipwhite

"bind :misc:hello:say_hello to CTRL-R
syn match xyzBind /bind\(!\)\?/ nextgroup=xyzBindPlugin skipwhite
syn match xyzBindPlugin /\(:\)\?\S\+/ nextgroup=xyzBindTo contained skipwhite
syn match xyzBindTo /to/ contained skipwhite

syn match xyzStatement /set chain key/

"highlight link xyzKeyword Keyword
highlight link xyzContext Keyword
highlight link xyzLoad Statement
highlight link xyzBind Statement
highlight link xyzBindTo Statement
highlight link xyzStatement Statement
highlight link xyzComment Comment
highlight link xyzNSPath Identifier
highlight link xyzPlugin Identifier
highlight link xyzBindPlugin Identifier
